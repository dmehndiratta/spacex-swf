"""Part IV — accrual / mark-to-market tax models (plan.md §7.5).

Standalone evaluation of a tax on the unrealized gains of the very wealthy.
  - unrealized_gains_by_bucket() : the stock of unrealized gains by wealth percentile (DFA/SCF).
  - revenue_estimate()           : annual revenue from an accrual tax, with avoidance/migration
                                   elasticity and a symmetric loss-refund drag.
  - buy_borrow_die()             : worked example of the loophole vs an accrual tax.
  - symmetry_illustration()      : gain vs loss years, with and without loss remuneration.

Designed so the dashboards can re-run the revenue + symmetry math client-side; this provides
the base calibration and reference numbers.
"""
from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import pandas as pd
from swf import paths


def unrealized_gains_by_bucket() -> dict:
    df = pd.read_csv(paths.DATA / "seeds" / "wealth_unrealized.csv", comment="#")
    df["unrealized_t"] = (df["net_worth_t"] * df["unrealized_share"]).round(1)
    total_ur = float(df["unrealized_t"].sum())
    top01 = float(df.loc[df["bucket"] == "Top 0.1%", "unrealized_t"].iloc[0])
    top1 = float(df.loc[df["bucket"].isin(["Top 0.1%", "Top 0.1-1%"]), "unrealized_t"].sum())
    return {
        "buckets": df.to_dict("records"),
        "total_unrealized_t": round(total_ur, 1),
        "top01_unrealized_t": round(top01, 1),
        "top1_unrealized_t": round(top1, 1),
        "top1_share_of_unrealized": round(top1 / total_ur, 3),
    }


def revenue_estimate(threshold: str = "1B", rate: float = 0.25, expected_return: float = 0.07,
                     avoidance: float = 0.25, loss_refund_drag: float = 0.15) -> dict:
    """Annual revenue ≈ taxable base × expected return × rate × (1 − avoidance) × (1 − loss drag).
    Base = the unrealized-gains stock held above the threshold tier."""
    g = unrealized_gains_by_bucket()
    # taxable stock by threshold tier
    base_t = g["top01_unrealized_t"] if threshold == "1B" else g["top1_unrealized_t"]
    n_taxpayers = 800 if threshold == "1B" else 25000  # rough: billionaires vs >$100M households
    annual_accrual_t = base_t * expected_return
    gross_rev_t = annual_accrual_t * rate
    net_rev_t = gross_rev_t * (1 - avoidance) * (1 - loss_refund_drag)
    return {
        "threshold": threshold, "rate": rate, "expected_return": expected_return,
        "avoidance": avoidance, "loss_refund_drag": loss_refund_drag,
        "taxable_stock_t": round(base_t, 1), "n_taxpayers": n_taxpayers,
        "annual_accrual_t": round(annual_accrual_t, 2),
        "gross_revenue_bn": round(gross_rev_t * 1000, 0),
        "net_revenue_bn": round(net_rev_t * 1000, 0),
        "revenue_10yr_bn": round(net_rev_t * 1000 * 10, 0),
    }


def buy_borrow_die(start_value: float = 1000.0, growth: float = 0.10, years: int = 20,
                   ltcg_rate: float = 0.238, accrual_rate: float = 0.25) -> dict:
    """Compare lifetime tax under (a) buy-borrow-die with stepped-up basis at death (=$0 income
    tax on the gain) vs (b) annual accrual taxation."""
    end_value = start_value * (1 + growth) ** years
    gain = end_value - start_value
    # (a) buy-borrow-die: borrow against the asset, never realize, step-up at death -> $0 gain tax
    bbd_tax = 0.0
    # (b) annual accrual: tax each year's gain at accrual_rate
    v, accrual_tax = start_value, 0.0
    for _ in range(years):
        yr_gain = v * growth
        accrual_tax += yr_gain * accrual_rate
        v += yr_gain
    return {
        "start_value": start_value, "end_value": round(end_value, 0), "gain": round(gain, 0),
        "growth": growth, "years": years,
        "buy_borrow_die_tax": round(bbd_tax, 0),
        "naive_realization_tax": round(gain * ltcg_rate, 0),
        "accrual_tax_total": round(accrual_tax, 0),
        "ltcg_rate": ltcg_rate, "accrual_rate": accrual_rate,
    }


def symmetry_illustration() -> dict:
    """A volatile asset over 6 years: show tax paid with a one-sided tax (gains only) vs a
    symmetric tax (gains taxed, losses refunded/credited). Returns per-year cashflows."""
    returns = [0.30, -0.20, 0.40, -0.30, 0.25, 0.15]
    rate = 0.25
    v_one = v_sym = 100.0
    rows = []
    cum_one = cum_sym = 0.0
    for i, r in enumerate(returns, 1):
        gain_one = v_one * r
        tax_one = max(0.0, gain_one) * rate          # one-sided: only taxes gains
        gain_sym = v_sym * r
        tax_sym = gain_sym * rate                     # symmetric: negative tax = refund in loss years
        cum_one += tax_one
        cum_sym += tax_sym
        rows.append({"year": i, "return_pct": round(r * 100), "tax_one_sided": round(tax_one, 1),
                     "tax_symmetric": round(tax_sym, 1), "cum_one": round(cum_one, 1),
                     "cum_sym": round(cum_sym, 1)})
        v_one *= (1 + r)
        v_sym *= (1 + r)
    return {"rows": rows, "rate": rate,
            "total_one_sided": round(cum_one, 1), "total_symmetric": round(cum_sym, 1)}


if __name__ == "__main__":
    g = unrealized_gains_by_bucket()
    print(f"Unrealized gains: total ${g['total_unrealized_t']}T, top 1% ${g['top1_unrealized_t']}T "
          f"({g['top1_share_of_unrealized']*100:.0f}% of all unrealized gains)")
    r = revenue_estimate()
    print(f"Revenue ($1B tier, 25%): ${r['net_revenue_bn']:.0f}B/yr net, ${r['revenue_10yr_bn']:.0f}B/10yr")
    print("Buy-borrow-die:", buy_borrow_die())
    s = symmetry_illustration()
    print(f"Symmetry: one-sided ${s['total_one_sided']} vs symmetric ${s['total_symmetric']}")
