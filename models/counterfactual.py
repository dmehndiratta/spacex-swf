"""Part II models (plan.md §5.2).

  - tarp_counterfactual() : the 2008 "kept-it" counterfactual. For each rescued firm, compare
    what Treasury ACTUALLY realized (sold the stake 2009-2014) against a 'kept-it' value:
    the realized proceeds reinvested in a broad market index (S&P 500) from the disposition
    date to today. The gap is the upside the public forfeited by selling early.
    Labelled an *illustrative counterfactual*, not an identified causal estimate.

  - spacex_support_ledger() : SpaceX's public scaffolding — identified federal obligations
    (USAspending), FCC RDOF (rescinded), and state/local incentives.

  - equity_condition_estimate() : if a warrant-priced equity condition had attached to that
    support, a transparent formula for the stake the public fund would hold today.
"""
from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import pandas as pd
from swf import paths


def _spx_multiple_since(date, latest_close, spx):
    d = pd.Timestamp(date)
    prior = spx[spx["date"] <= d]
    base = float(prior["close"].iloc[-1]) if len(prior) else float(spx["close"].iloc[0])
    return latest_close / base


def tarp_counterfactual() -> dict:
    seed = pd.read_csv(paths.DATA / "seeds" / "tarp_bailouts.csv", comment="#")
    prices = pd.read_parquet(paths.PROCESSED / "prices.parquet")
    spx = prices[prices["ticker"] == "^GSPC"].sort_values("date")
    latest = float(spx["close"].iloc[-1])
    latest_date = str(spx["date"].iloc[-1].date())

    rows = []
    for _, r in seed.iterrows():
        mult = _spx_multiple_since(r["disposition_date"], latest, spx)
        kept = r["realized_proceeds_bn"] * mult
        rows.append({
            "program": r["program"], "disbursed_bn": round(r["disbursed_bn"], 1),
            "realized_bn": round(r["realized_proceeds_bn"], 1),
            "realized_pnl_bn": round(r["realized_proceeds_bn"] - r["disbursed_bn"], 1),
            "disposition": r["disposition_date"][:7],
            "spx_multiple": round(mult, 2),
            "kept_value_bn": round(kept, 1),
            "forfeited_bn": round(kept - r["realized_proceeds_bn"], 1),
            "note": r["note"],
        })
    tot_disb = sum(x["disbursed_bn"] for x in rows)
    tot_real = sum(x["realized_bn"] for x in rows)
    tot_kept = sum(x["kept_value_bn"] for x in rows)
    return {
        "rows": rows, "as_of": latest_date,
        "total_disbursed_bn": round(tot_disb, 1),
        "total_realized_bn": round(tot_real, 1),
        "total_realized_pnl_bn": round(tot_real - tot_disb, 1),
        "total_kept_value_bn": round(tot_kept, 1),
        "total_forfeited_bn": round(tot_kept - tot_real, 1),
        "index": "S&P 500 (price; understates total return)",
    }


def spacex_support_ledger() -> dict:
    aw_path = paths.PROCESSED / "spacex_awards.parquet"
    federal_bn = float(pd.read_parquet(aw_path)["amount"].sum() / 1e9) if aw_path.exists() else 0.0
    sub = pd.read_csv(paths.DATA / "seeds" / "subsidies_statelocal.csv", comment="#")
    spacex_sub = sub[sub["entity"] == "SpaceX"]
    received_m = float(spacex_sub.loc[spacex_sub["status"] == "received", "amount_m"].sum())
    rescinded_m = float(spacex_sub.loc[spacex_sub["status"] == "rescinded", "amount_m"].sum())
    return {
        "federal_contracts_bn": round(federal_bn, 1),
        "statelocal_received_m": round(received_m, 1),
        "rescinded_m": round(rescinded_m, 1),
        "total_support_bn": round(federal_bn + received_m / 1000, 1),
        "items": [
            {"label": "Federal contracts (NASA + DoD, identified)", "bn": round(federal_bn, 1),
             "kind": "contract"},
            {"label": "State/local incentives received", "bn": round(received_m / 1000, 2),
             "kind": "subsidy"},
            {"label": "FCC RDOF award (rescinded)", "bn": round(rescinded_m / 1000, 2),
             "kind": "rescinded"},
        ],
    }


def equity_condition_estimate(stake_rate: float = 0.10) -> dict:
    """Illustrative: if `stake_rate` of material support had converted to a (warrant-priced)
    equity claim, what would the public fund hold today? We grow the claim with SpaceX's
    valuation since the support. Contracts are payment for services, so we apply the condition
    only to the SUBSIDY-LIKE share (a fraction of contracts behaves as de-facto subsidy via
    cost-plus margin + market-making demand); this is exposed as a slider in the dashboard."""
    led = spacex_support_ledger()
    # Treat identified federal support's de-facto-subsidy component as `subsidy_share` of contracts
    subsidy_share = 0.25  # conservative: a quarter of contract value as effective public underwriting
    base_support_bn = led["federal_contracts_bn"] * subsidy_share + led["statelocal_received_m"] / 1000
    # SpaceX valuation appreciation since the support period (~2012 avg) to the $1.77T IPO mark.
    # A $1.77T company vs an early-2010s valuation of order $10-20B -> ~50-100x. Use a conservative 30x.
    appreciation = 30.0
    stake_today_bn = base_support_bn * stake_rate * appreciation
    return {
        "stake_rate": stake_rate, "subsidy_share": subsidy_share, "appreciation": appreciation,
        "base_support_bn": round(base_support_bn, 2),
        "stake_today_bn": round(stake_today_bn, 1),
        "note": "Illustrative. Stake = subsidy-equivalent support x stake-rate x valuation appreciation.",
    }


if __name__ == "__main__":
    import json
    t = tarp_counterfactual()
    print(f"TARP: disbursed ${t['total_disbursed_bn']}B, realized ${t['total_realized_bn']}B "
          f"(P&L ${t['total_realized_pnl_bn']:+}B), kept-it ${t['total_kept_value_bn']}B, "
          f"forfeited ${t['total_forfeited_bn']}B")
    print("SpaceX support:", json.dumps(spacex_support_ledger(), indent=2))
    print("Equity-condition (10%):", equity_condition_estimate())
