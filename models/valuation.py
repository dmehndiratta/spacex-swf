"""Valuation models for Part I (plan.md §4.2).

No positive earnings -> value from sales, segments, and scenarios, not P/E.
  - sotp_base()      : sum-of-the-parts with explicit per-segment assumptions
  - reverse_dcf()    : solve the revenue CAGR the price implies at a given margin/WACC
  - reverse_dcf_grid : the "what you must believe" sensitivity surface
  - scenario_dcf()   : explicit bull / base / bear with stated drivers + probabilities

All base inputs trace to data/facts/ipo_facts.yaml; multiples are analyst assumptions,
flagged as such and exposed as dashboard sliders.
"""
from __future__ import annotations
from dataclasses import dataclass, asdict


# --- Sum of the parts -------------------------------------------------------
# Each segment: (label, base FY revenue $B, near-term growth, {bear,base,bull} EV/forward-sales)
# Forward sales = base_rev * (1+growth). Multiples reflect the segment's quality/growth.
SEGMENTS = {
    "starlink": dict(
        label="Starlink (connectivity)",
        rev_bn=11.4, growth=0.50,
        mult={"bear": 9, "base": 15, "bull": 26},
        note="Profitable engine: $4.4B op income, 9M+ subs, direct-to-cell + global-broadband TAM. "
             "Valued on forward EV/Sales like a high-growth connectivity/subscription business.",
    ),
    "launch": dict(
        label="Launch (Falcon / Starship)",
        rev_bn=5.8, growth=0.20,
        mult={"bear": 5, "base": 9, "bull": 16},
        note="Dominant cadence, contracted backlog, falling $/kg. Bull multiple carries Starship "
             "heavy-lift / Mars optionality; bear treats it as a cyclical gov-contract launcher.",
    ),
    "xai": dict(
        label="xAI (AI segment)",
        rev_bn=1.5, growth=1.00,
        mult={"bear": 25, "base": 70, "bull": 150},
        note="Loss-making ($6.35B op loss, $12.7B capex). Valued against frontier-AI private marks "
             "with a wide band — explicit option-value-vs-cash-burn. Bear ~ a token mark; bull ~ a "
             "top-tier frontier lab.",
    ),
}


def sotp_segment(seg: dict, case: str) -> float:
    fwd_sales = seg["rev_bn"] * (1 + seg["growth"])
    return fwd_sales * seg["mult"][case]


def sotp_base() -> dict:
    out = {"segments": {}, "totals": {}}
    for key, seg in SEGMENTS.items():
        vals = {c: round(sotp_segment(seg, c), 1) for c in ("bear", "base", "bull")}
        out["segments"][key] = {
            "label": seg["label"], "rev_bn": seg["rev_bn"], "growth": seg["growth"],
            "mult": seg["mult"], "note": seg["note"], "ev_bn": vals,
        }
    for c in ("bear", "base", "bull"):
        out["totals"][c] = round(sum(sotp_segment(s, c) for s in SEGMENTS.values()), 1)
    return out


# --- Reverse DCF ("what you must believe") ----------------------------------
@dataclass
class DCFInputs:
    base_rev_bn: float = 18.7        # FY2025 revenue
    target_ev_bn: float = 1770.0     # the ~$1.77T headline
    years: int = 10                  # explicit forecast horizon
    ss_margin: float = 0.20          # steady-state FCF margin reached by year `years`
    wacc: float = 0.11               # discount rate (long-duration name)
    term_growth: float = 0.03        # perpetuity growth after the horizon


def _ev_from_cagr(g: float, p: DCFInputs) -> float:
    """PV of FCF over the horizon + terminal value, given an initial revenue CAGR g.
    FCF margin ramps linearly from a small start to the steady-state margin by year `years`."""
    rev = p.base_rev_bn
    pv = 0.0
    start_margin = 0.02
    for t in range(1, p.years + 1):
        rev *= (1 + g)
        margin = start_margin + (p.ss_margin - start_margin) * (t / p.years)
        fcf = rev * margin
        pv += fcf / (1 + p.wacc) ** t
    # terminal value on year-N FCF
    fcf_n = rev * p.ss_margin
    tv = fcf_n * (1 + p.term_growth) / (p.wacc - p.term_growth)
    pv += tv / (1 + p.wacc) ** p.years
    return pv


def implied_cagr(p: DCFInputs) -> float:
    """Bisect for the revenue CAGR that makes PV == target EV."""
    lo, hi = 0.0, 2.0
    for _ in range(80):
        mid = (lo + hi) / 2
        if _ev_from_cagr(mid, p) < p.target_ev_bn:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def reverse_dcf_grid(margins=(0.15, 0.20, 0.25, 0.30),
                     waccs=(0.09, 0.10, 0.11, 0.12, 0.13),
                     base: DCFInputs | None = None) -> dict:
    base = base or DCFInputs()
    grid = []
    for m in margins:
        row = []
        for w in waccs:
            p = DCFInputs(base_rev_bn=base.base_rev_bn, target_ev_bn=base.target_ev_bn,
                          years=base.years, ss_margin=m, wacc=w, term_growth=base.term_growth)
            row.append(round(implied_cagr(p) * 100, 1))
        grid.append(row)
    return {
        "margins": [round(m * 100) for m in margins],
        "waccs": [round(w * 100, 1) for w in waccs],
        "implied_cagr_pct": grid,
        "base_case": {"ss_margin": base.ss_margin, "wacc": base.wacc,
                      "implied_cagr_pct": round(implied_cagr(base) * 100, 1)},
        "inputs": asdict(base),
    }


# --- Scenario DCF -----------------------------------------------------------
SCENARIOS = {
    "bull": dict(prob=0.25, cagr=0.47, ss_margin=0.30, wacc=0.10,
                 belief="Starlink becomes the global connectivity layer (direct-to-cell at scale), "
                        "Starship collapses $/kg and opens new markets, and xAI is a top-3 frontier "
                        "lab. This is the case the market price already embeds — it roughly "
                        "rationalises the $1.77T mark."),
    "base": dict(prob=0.50, cagr=0.35, ss_margin=0.22, wacc=0.11,
                 belief="Starlink keeps compounding into profitability, launch grows steadily, xAI is "
                        "a credible but cash-hungry challenger. A great company — worth well under the "
                        "market mark."),
    "bear": dict(prob=0.25, cagr=0.24, ss_margin=0.16, wacc=0.125,
                 belief="Starlink growth decelerates as it saturates dense markets and faces Kuiper, "
                        "Starship slips, and xAI burns without winning — the AI/space narrative compresses."),
}


def scenario_dcf() -> dict:
    out = {"scenarios": {}}
    ev_weighted = 0.0
    for name, s in SCENARIOS.items():
        p = DCFInputs(ss_margin=s["ss_margin"], wacc=s["wacc"])
        ev = _ev_from_cagr(s["cagr"], p)
        out["scenarios"][name] = {
            "prob": s["prob"], "cagr_pct": round(s["cagr"] * 100, 1),
            "ss_margin_pct": round(s["ss_margin"] * 100, 1), "wacc_pct": round(s["wacc"] * 100, 1),
            "implied_ev_bn": round(ev, 0), "belief": s["belief"],
        }
        ev_weighted += s["prob"] * ev
    out["prob_weighted_ev_bn"] = round(ev_weighted, 0)
    out["market_ev_bn"] = 1770.0
    return out


if __name__ == "__main__":
    import json
    print("SOTP:", json.dumps(sotp_base()["totals"]))
    print("Reverse-DCF base implied CAGR %:", reverse_dcf_grid()["base_case"])
    sd = scenario_dcf()
    print("Scenario prob-weighted EV $B:", sd["prob_weighted_ev_bn"], "vs market", sd["market_ev_bn"])
