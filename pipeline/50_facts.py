"""Stage 50 — regenerate the facts JSON the MDX imports, so prose and dashboards read the
same numbers (plan.md §9.1: no number hard-coded twice) and the page carries a live
'last updated' timestamp + tracker summary.

Writes to ../../src/data/spacex_facts.json (committed; consumed by the MDX via import)."""
from __future__ import annotations
import sys, json, datetime as dt
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from swf import paths, facts as facts_mod

OUT = paths.SITE_ROOT / "src" / "data" / "spacex_facts.json"


def log(m): print(f"[50_facts] {m}", flush=True)


def ordinal(n: int) -> str:
    if 10 <= n % 100 <= 20:
        suf = "th"
    else:
        suf = {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}{suf}"


def tb(bn: float) -> str:
    """Format a $billions figure as $XXXB below a trillion, $X.XXT above."""
    return f"${bn/1000:.2f}T" if abs(bn) >= 1000 else f"${bn:.0f}B"


def main():
    f = facts_mod.load()
    h = f.human_usd
    bundle = json.loads((paths.PROCESSED / "part1_models.json").read_text(encoding="utf-8"))
    sc_path = paths.PROCESSED / "scorecard.json"
    sc = json.loads(sc_path.read_text(encoding="utf-8")) if sc_path.exists() else {}

    rd = bundle["reverse_dcf"]["base_case"]
    sotp = bundle["sotp"]["totals"]
    p2_path = paths.PROCESSED / "part2_models.json"
    p2 = json.loads(p2_path.read_text(encoding="utf-8")) if p2_path.exists() else {}
    p3_path = paths.PROCESSED / "part3_models.json"
    p3 = json.loads(p3_path.read_text(encoding="utf-8")) if p3_path.exists() else {}
    p4_path = paths.PROCESSED / "part4_models.json"
    p4 = json.loads(p4_path.read_text(encoding="utf-8")) if p4_path.exists() else {}
    out = {
        "lastUpdated": dt.date.today().isoformat(),
        "nextRefresh": "weekly (Mondays, via GitHub Actions)",
        # offering
        "ticker": f.get("offering.ticker"),
        "ipoPrice": f"${f.get('offering.ipo_price_usd'):.0f}",
        "sharesOffered": f"{f.get('offering.shares_offered')/1e6:.1f}M",
        "grossProceeds": h(f.get("offering.gross_proceeds_usd")),
        "greenshoe": h(f.get("offering.greenshoe_proceeds_usd")),
        "valuation": h(f.get("offering.implied_valuation_usd")),
        "firstTradeDate": str(f.get("offering.first_trade_date")),
        # first day
        "openPrice": f"${f.get('first_day.open_usd'):.0f}",
        "closePrice": f"${f.get('first_day.close_usd'):.2f}",
        "firstDayPct": f"+{f.get('first_day.close_pct_vs_ipo')*100:.1f}%",
        "intradayHigh": f"${f.get('first_day.intraday_high_usd'):.2f}",
        "underpricingNotional": h(f.get("first_day.underpricing_notional_usd")),
        # financials
        "revenue": h(f.get("financials_fy2025.revenue_total_usd")),
        "netLoss": h(abs(f.get("financials_fy2025.net_loss_usd"))),
        "psTrailing": f"{f.get('financials_fy2025.implied_ps_trailing'):.0f}×",
        "starlinkRevenue": h(f.get("financials_fy2025.starlink.revenue_usd")),
        "starlinkOpIncome": h(f.get("financials_fy2025.starlink.operating_income_usd")),
        "starlinkUsers": f"{f.get('financials_fy2025.starlink.users_end_2025')/1e6:.0f}M+",
        "xaiOpLoss": h(abs(f.get("financials_fy2025.ai_segment_xai.operating_loss_usd"))),
        "xaiCapex": h(f.get("financials_fy2025.ai_segment_xai.capex_usd")),
        # context
        "priorRecord": f.get("context.prior_record_ipo.name"),
        "priorRecordProceeds": h(f.get("context.prior_record_ipo.gross_proceeds_usd")),
        "spacexMultipleOfRecord": f"{f.get('context.prior_record_ipo.spacex_multiple_of_record'):.1f}×",
        # model outputs (single source = part1_models.json)
        "sotpBear": tb(sotp["bear"]), "sotpBase": tb(sotp["base"]), "sotpBull": tb(sotp["bull"]),
        "reverseDcfCagr": f"{rd['implied_cagr_pct']:.0f}%",
        "reverseDcfMargin": f"{int(rd['ss_margin']*100)}%",
        "reverseDcfWacc": f"{int(rd['wacc']*100)}%",
        "scenarioProbWeightedEv": tb(bundle["scenario_dcf"]["prob_weighted_ev_bn"]),
        "firstDayPercentile": ordinal(int(bundle["first_day_pop"]["percentile"])),
        "firstDayMedian": f"+{bundle['first_day_pop']['median']*100:.0f}%",
        "nRisks": bundle["risk_register"]["n"],
        "floatPctOfTotal": f"{bundle['lockup']['float_pct_of_total']:.1f}%",
        "lockup180Value": tb([t["value_bn"] for t in bundle["lockup"]["tranches"] if t["day"] == 180][0]),
        # tracker
        "trackerSpcxLast": f"${sc.get('spcx_last_close', 0):.2f}" if sc.get("spcx_last_close") else "n/a",
        "trackerVsIpo": f"{sc.get('spcx_vs_ipo_pct', 0):+.1f}%" if sc.get("spcx_vs_ipo_pct") is not None else "n/a",
        "trackerDays": sc.get("days_since_ipo", 0),
    }
    if p2:
        t, led = p2["tarp"], p2["spacex_support"]
        out.update({
            "spacexFederalSupport": tb(led["federal_contracts_bn"]),
            "spacexTotalSupport": tb(led["total_support_bn"]),
            "rdofRescinded": f"${led['rescinded_m']:.1f}M",
            "tarpDisbursed": tb(t["total_disbursed_bn"]),
            "tarpRealized": tb(t["total_realized_bn"]),
            "tarpRealizedPnl": ("+" if t["total_realized_pnl_bn"] >= 0 else "") + tb(t["total_realized_pnl_bn"]),
            "tarpKeptValue": tb(t["total_kept_value_bn"]),
            "tarpForfeited": tb(t["total_forfeited_bn"]),
            "equityStakeToday": tb(p2["equity_condition"]["stake_today_bn"]),
        })
    if p3:
        fb = p3["fundsim_base"]
        out.update({
            "fundAum30y": tb(fb["end_aum_bn"]),
            "fundDividend30y": f"${fb['end_dividend_per_capita']:.0f}",
            "fundPayout30y": tb(fb["end_payout_bn"]),
            "fundInflow": tb(fb["params"]["annual_inflow_bn"]),
            "fundDrawdownAum": tb(p3["fundsim_drawdown"]["end_aum_bn"]),
        })
        ew = p3.get("economy_wide")
        if ew:
            out.update({
                "ewCompanies": ew["n_companies"],
                "ewSectors": ew["n_sectors"],
                "ewSubsidies": tb(ew["total_subsidy_bn"]),
                "ewPortfolio3x": tb(ew["total_subsidy_bn"] * ew["default_value_multiple"]),
            })
    if p4:
        u, r1 = p4["unrealized"], p4["revenue_1b"]
        out.update({
            "unrealizedTotal": f"${u['total_unrealized_t']:.0f}T",
            "unrealizedTop1": f"${u['top1_unrealized_t']:.0f}T",
            "unrealizedTop1Share": f"{u['top1_share_of_unrealized']*100:.0f}%",
            "taxRevenueYr": tb(r1["net_revenue_bn"]),
            "taxRevenue10yr": tb(r1["revenue_10yr_bn"]),
            "symOneSided": f"${p4['symmetry']['total_one_sided']:.0f}",
            "symSymmetric": f"${p4['symmetry']['total_symmetric']:.0f}",
        })
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, indent=2), encoding="utf-8")
    log(f"wrote {OUT.relative_to(paths.SITE_ROOT)} ({len(out)} fields), lastUpdated={out['lastUpdated']}")


if __name__ == "__main__":
    main()
