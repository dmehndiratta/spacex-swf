"""Market structure, flows, and price discovery for Part I (plan.md §4.5).

  - lockup_waterfall() : staged share-unlock schedule + the supply shock at each tranche,
                         sized against average daily volume (days-to-absorb).
  - index_inclusion()  : Nasdaq-100 fast-track + S&P 500 (GAAP-profitability gate) timing,
                         and the passive demand a ~$1.77T addition creates (AUM x weight).

Lockup terms and float are modelled from the seed assumptions below until the exact
prospectus schedule is pinned in Phase 8; every assumption is exposed in the dashboard.
"""
from __future__ import annotations

# --- float / share-count assumptions (from offering + typical structure) ---
SHARES_OFFERED = 555_555_555          # the IPO float (primary)
GREENSHOE = 83_333_333
# SpaceX is ~ a $1.77T cap at $135 => ~13.1B fully-diluted shares.
TOTAL_SHARES = round(1.77e12 / 135.0)  # ~13.11B
PUBLIC_FLOAT_AT_IPO = SHARES_OFFERED + GREENSHOE
INSIDER_LOCKED = TOTAL_SHARES - PUBLIC_FLOAT_AT_IPO

# First-day dollar volume was heavy; assume a normalising ADV (shares/day) for absorption math.
ADV_SHARES = 30_000_000  # modelled steady-state average daily volume


def lockup_waterfall() -> dict:
    """Staged release: the standard 180-day cliff, split with an early price-trigger tranche
    and an employee tranche, plus the eventual founder-controlled overhang."""
    price = 161.0  # ~ first-day close, for $ sizing
    tranches = [
        dict(day=90,  label="Early release (price trigger)", frac_of_locked=0.10,
             note="Common 90-day partial release if the stock holds >X% above IPO price."),
        dict(day=180, label="Main lockup expiry", frac_of_locked=0.35,
             note="The classic 180-day cliff — the largest single supply event."),
        dict(day=270, label="Employee / RSU tranche", frac_of_locked=0.15,
             note="Staggered staff selling once trading windows open."),
        dict(day=365, label="Remaining insider overhang", frac_of_locked=0.40,
             note="Founder-controlled stock; mostly retained, but the legal overhang lifts."),
    ]
    out = []
    for t in tranches:
        shares = int(INSIDER_LOCKED * t["frac_of_locked"])
        out.append({
            **t,
            "shares": shares,
            "value_bn": round(shares * price / 1e9, 1),
            "days_to_absorb": round(shares / ADV_SHARES, 1),
            "pct_of_float": round(shares / PUBLIC_FLOAT_AT_IPO * 100, 1),
        })
    return {
        "total_shares": TOTAL_SHARES, "public_float_ipo": PUBLIC_FLOAT_AT_IPO,
        "insider_locked": INSIDER_LOCKED, "adv_shares": ADV_SHARES,
        "float_pct_of_total": round(PUBLIC_FLOAT_AT_IPO / TOTAL_SHARES * 100, 1),
        "tranches": out,
    }


def index_inclusion() -> dict:
    """Passive demand = tracking AUM x target index weight. Two gates:
       Nasdaq-100 (no profitability requirement; fast-track ~ next reconstitution),
       S&P 500 (requires GAAP profitability over trailing 4 quarters -> likely delayed)."""
    mktcap_bn = 1770.0
    indices = [
        dict(index="Nasdaq-100", tracking_aun_bn=550, est_index_mktcap_bn=28000,
             eligible="Fast-track eligible (top non-financials); next special rebalance.",
             gate_passed=True),
        dict(index="S&P 500", tracking_aun_bn=11500, est_index_mktcap_bn=52000,
             eligible="Gated by GAAP profitability (trailing 4 quarters). Net loss -> delayed "
                      "until SpaceX prints sustained GAAP profit.",
             gate_passed=False),
    ]
    out = []
    for ix in indices:
        weight = mktcap_bn / ix["est_index_mktcap_bn"]
        passive_demand_bn = ix["tracking_aun_bn"] * weight
        out.append({
            **ix,
            "target_weight_pct": round(weight * 100, 2),
            "passive_demand_bn": round(passive_demand_bn, 1),
            "passive_demand_days_adv": round(passive_demand_bn * 1e9 / (ADV_SHARES * 161.0), 1),
        })
    return {"mktcap_bn": mktcap_bn, "indices": out}


if __name__ == "__main__":
    import json
    lw = lockup_waterfall()
    print("float % of total:", lw["float_pct_of_total"])
    for t in lw["tranches"]:
        print(f"  day {t['day']:>3}: {t['label']:<34} {t['shares']/1e6:6.0f}M  ${t['value_bn']}B  {t['days_to_absorb']}d ADV")
    print(json.dumps(index_inclusion()["indices"], indent=2))
