"""Stage 20 — run all models, write a per-part JSON bundle the dashboards read, and
freeze the Part I predictions once (the 'living' tracker scores against this snapshot).

Outputs:
  data/processed/part1_models.json   (valuation, event study, lockup, index flows, risk register)
  data/predictions/predictions.yaml  (frozen at first run; never silently overwritten)
"""
from __future__ import annotations
import sys, json, datetime as dt
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import yaml
from swf import paths, facts
from models import (valuation, eventstudy, marketstructure, riskregister, counterfactual,
                    fundsim, taxrevenue)


def log(m): print(f"[20_models] {m}", flush=True)


def build_part1() -> dict:
    f = facts.load()
    bundle = {
        "generated_at": dt.datetime.now().isoformat(timespec="seconds"),
        "facts": {
            "ipo_price": f.get("offering.ipo_price_usd"),
            "first_day_close": f.get("first_day.close_usd"),
            "valuation_bn": f.get("offering.implied_valuation_usd") / 1e9,
            "revenue_bn": f.get("financials_fy2025.revenue_total_usd") / 1e9,
            "ps_trailing": f.get("financials_fy2025.implied_ps_trailing"),
        },
        "sotp": valuation.sotp_base(),
        "reverse_dcf": valuation.reverse_dcf_grid(),
        "scenario_dcf": valuation.scenario_dcf(),
        "first_day_pop": eventstudy.first_day_pop_stats(),
        "event_study": eventstudy.peer_event_study(),
        "lockup": marketstructure.lockup_waterfall(),
        "index_inclusion": marketstructure.index_inclusion(),
        "risk_register": riskregister.risk_register(),
    }
    return bundle


def build_part2() -> dict:
    return {
        "generated_at": dt.datetime.now().isoformat(timespec="seconds"),
        "tarp": counterfactual.tarp_counterfactual(),
        "spacex_support": counterfactual.spacex_support_ledger(),
        "equity_condition": counterfactual.equity_condition_estimate(),
    }


# Each precedent is a holding period: the year public equity was TAKEN and the year it was SOLD.
# The proposal is the only one with no sale date — it is held in perpetuity.
PRECEDENTS = [
    {"label": "Chrysler bailout", "taken": 1979, "sold": 1983,
     "equity": "Warrants on the $1.2B federal loan guarantee",
     "outcome": "Sold back when Chrysler recovered; Treasury booked a gain and exited.",
     "kept": False},
    {"label": "TARP (AIG, GM, Citi, banks)", "taken": 2008, "sold": 2014,
     "equity": "Equity stakes and warrants across the rescued firms",
     "outcome": "Sold back 2009-2014, at the first politically convenient moment.",
     "kept": False},
    {"label": "UK RBS / Lloyds", "taken": 2008, "sold": 2018,
     "equity": "Majority stakes in two of Britain's largest banks",
     "outcome": "Disposed of gradually over the following decade.",
     "kept": False},
    {"label": "Proposed equity condition", "taken": 2026, "sold": None,
     "equity": "Stake matched to the public support that earned it",
     "outcome": "Retained and pooled in a Social Wealth Fund, in perpetuity.",
     "kept": True},
]


def build_part3() -> dict:
    return {
        "generated_at": dt.datetime.now().isoformat(timespec="seconds"),
        "fundsim_base": fundsim.simulate(),
        "fundsim_drawdown": fundsim.simulate(drawdown_year=15),
        "precedents": PRECEDENTS,
        "economy_wide": counterfactual.economy_wide_portfolio(),
        "us_adults": fundsim.US_ADULTS,
    }


def build_part4() -> dict:
    return {
        "generated_at": dt.datetime.now().isoformat(timespec="seconds"),
        "unrealized": taxrevenue.unrealized_gains_by_bucket(),
        "revenue_1b": taxrevenue.revenue_estimate(threshold="1B"),
        "revenue_100m": taxrevenue.revenue_estimate(threshold="100M"),
        "buy_borrow_die": taxrevenue.buy_borrow_die(),
        "symmetry": taxrevenue.symmetry_illustration(),
    }


def freeze_predictions(bundle: dict) -> None:
    """Write predictions.yaml ONCE. The frozen predictions are what 30_score.py grades."""
    if paths.PREDICTIONS_YAML.exists():
        log(f"predictions already frozen at {paths.PREDICTIONS_YAML.name} — not overwriting")
        return
    sd = bundle["scenario_dcf"]["scenarios"]
    preds = {
        "frozen_at": dt.date.today().isoformat(),
        "subject": "SPCX",
        "benchmark": "^NDX",
        "ipo_price": bundle["facts"]["ipo_price"],
        "first_day_close": bundle["facts"]["first_day_close"],
        "notes": "Falsifiable Part I calls, frozen at publish. Scored weekly by 30_score.py. "
                 "Bands are judgemental, not model confidence intervals.",
        "predictions": [
            {"id": "ret_3m_vs_ndx", "horizon": "3 months",
             "statement": "SPCX 3-month total return relative to the Nasdaq-100",
             "point_pct": -8.0, "band_pct": [-25.0, 10.0],
             "rationale": "Mega-IPO post-debut drift is negative on average (Ritter); reverse-DCF "
                          "shows price embeds ~56% CAGR — little room for upside surprise near term."},
            {"id": "ret_12m_vs_ndx", "horizon": "12 months",
             "statement": "SPCX 12-month total return relative to the Nasdaq-100",
             "point_pct": -15.0, "band_pct": [-45.0, 20.0],
             "rationale": "Long-run mega-IPO underperformance + lockup supply + valuation gap to a "
                          "prob-weighted SOTP/DCF of ~$460-530B vs the $1.77T mark."},
            {"id": "lockup_180d_reaction", "horizon": "~180 days",
             "statement": "Sign of the abnormal return in the [-2,+5] window around the 180-day lockup expiry",
             "point_pct": -6.0, "band_pct": [-15.0, 2.0],
             "rationale": "Largest single supply event (~$700B notional, 145 ADV-days); literature "
                          "finds negative abnormal returns around large unlocks."},
            {"id": "peer_spillover_space", "horizon": "1 month",
             "statement": "Mean CAR for listed space/satellite peers over the month after the debut",
             "point_pct": 2.0, "band_pct": [-4.0, 8.0],
             "rationale": "Positive read-through (sector legitimisation / capital attention) modestly "
                          "outweighs liquidity diversion in the near term."},
        ],
        "scenario_fan": {
            "bull": {"prob": sd["bull"]["prob"], "ev_bn": sd["bull"]["implied_ev_bn"]},
            "base": {"prob": sd["base"]["prob"], "ev_bn": sd["base"]["implied_ev_bn"]},
            "bear": {"prob": sd["bear"]["prob"], "ev_bn": sd["bear"]["implied_ev_bn"]},
        },
    }
    paths.PREDICTIONS_YAML.parent.mkdir(parents=True, exist_ok=True)
    with open(paths.PREDICTIONS_YAML, "w", encoding="utf-8") as fh:
        yaml.safe_dump(preds, fh, sort_keys=False, allow_unicode=True)
    log(f"froze {len(preds['predictions'])} predictions -> {paths.PREDICTIONS_YAML.name}")


def main():
    paths.PROCESSED.mkdir(parents=True, exist_ok=True)
    bundle = build_part1()
    out = paths.PROCESSED / "part1_models.json"
    out.write_text(json.dumps(bundle, indent=2), encoding="utf-8")
    log(f"wrote {out.name}")

    p2 = build_part2()
    (paths.PROCESSED / "part2_models.json").write_text(json.dumps(p2, indent=2), encoding="utf-8")
    log(f"wrote part2_models.json: TARP forfeited ${p2['tarp']['total_forfeited_bn']}B; "
        f"SpaceX support ${p2['spacex_support']['total_support_bn']}B")

    p3 = build_part3()
    (paths.PROCESSED / "part3_models.json").write_text(json.dumps(p3, indent=2), encoding="utf-8")
    log(f"wrote part3_models.json: fund 30y AUM ${p3['fundsim_base']['end_aum_bn']/1000:.2f}T, "
        f"dividend ${p3['fundsim_base']['end_dividend_per_capita']:.0f}/adult")

    p4 = build_part4()
    (paths.PROCESSED / "part4_models.json").write_text(json.dumps(p4, indent=2), encoding="utf-8")
    log(f"wrote part4_models.json: unrealized ${p4['unrealized']['total_unrealized_t']}T, "
        f"$1B-tier net revenue ${p4['revenue_1b']['net_revenue_bn']:.0f}B/yr")
    log(f"  SOTP totals $B: {bundle['sotp']['totals']}")
    log(f"  reverse-DCF base implied CAGR: {bundle['reverse_dcf']['base_case']['implied_cagr_pct']}%")
    log(f"  scenario prob-weighted EV $B: {bundle['scenario_dcf']['prob_weighted_ev_bn']}")
    log(f"  first-day pop percentile: {bundle['first_day_pop']['percentile']}")
    log(f"  risks: {bundle['risk_register']['n']} (mean sev {bundle['risk_register']['mean_severity']})")
    freeze_predictions(bundle)
    log("done")


if __name__ == "__main__":
    main()
