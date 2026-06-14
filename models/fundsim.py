"""Part III — the Social Wealth Fund growth simulator (plan.md §6.6).

Projects fund AUM, annual distributions, and per-capita citizen dividend from:
  - annual inflow driven by the equity-condition rule ($bn/yr, optionally growing)
  - a real return assumption (calibrated to GPFG's long-run ~6% nominal / ~4-5% real)
  - a spending/dividend rule (% of fund/yr, Norway ~3%)
  - a horizon, with a 2008-style drawdown stress option.

Pure function so the dashboard can re-run it client-side; this module provides the base
calibration and a reference projection.
"""
from __future__ import annotations

US_ADULTS = 258_000_000  # ~ US adult population, for per-capita dividend
GPFG_REAL_RETURN = 0.05  # long-run real return calibration


def simulate(annual_inflow_bn: float = 60.0, inflow_growth: float = 0.02,
             real_return: float = GPFG_REAL_RETURN, payout_rate: float = 0.03,
             years: int = 30, start_aum_bn: float = 0.0,
             drawdown_year: int | None = None, drawdown_pct: float = 0.35) -> dict:
    aum = start_aum_bn
    inflow = annual_inflow_bn
    path = []
    for y in range(1, years + 1):
        aum *= (1 + real_return)
        if drawdown_year and y == drawdown_year:
            aum *= (1 - drawdown_pct)
        aum += inflow
        payout = aum * payout_rate
        aum -= payout
        path.append({
            "year": y, "aum_bn": round(aum, 1), "payout_bn": round(payout, 2),
            "dividend_per_capita": round(payout * 1e9 / US_ADULTS, 0),
        })
        inflow *= (1 + inflow_growth)
    end = path[-1]
    return {
        "params": {"annual_inflow_bn": annual_inflow_bn, "inflow_growth": inflow_growth,
                   "real_return": real_return, "payout_rate": payout_rate, "years": years,
                   "drawdown_year": drawdown_year, "drawdown_pct": drawdown_pct},
        "path": path,
        "end_aum_bn": end["aum_bn"], "end_payout_bn": end["payout_bn"],
        "end_dividend_per_capita": end["dividend_per_capita"],
        "us_adults": US_ADULTS,
    }


if __name__ == "__main__":
    r = simulate()
    print(f"30y: AUM ${r['end_aum_bn']/1000:.2f}T, annual payout ${r['end_payout_bn']:.0f}B, "
          f"dividend ${r['end_dividend_per_capita']:.0f}/adult/yr")
    r2 = simulate(drawdown_year=15)
    print(f"with 2008-style drawdown yr15: AUM ${r2['end_aum_bn']/1000:.2f}T")
