"""Stage 30 — the 'living analysis' scorer (plan.md §11).

Pulls realised SPCX + benchmark returns, grades each frozen prediction whose horizon has
elapsed (pending / within band / outside band), updates a scorecard JSON, and appends a
dated line to a public changelog.
"""
from __future__ import annotations
import sys, json, datetime as dt
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import pandas as pd
import yaml
from swf import paths

CHANGELOG = paths.PROCESSED / "tracker_changelog.md"
SCORECARD = paths.PROCESSED / "scorecard.json"
IPO_DATE = pd.Timestamp("2026-06-12")


def log(m): print(f"[30_score] {m}", flush=True)


def _series(prices, tk):
    return prices[prices["ticker"] == tk].sort_values("date").set_index("date")["close"]


def _ret_over(series, start, days):
    """Total return from the first quote on/after `start` to the last quote on/before start+days."""
    end = start + pd.Timedelta(days=days)
    s = series[(series.index >= start) & (series.index <= end)]
    if len(s) < 2:
        return None
    return float(s.iloc[-1] / s.iloc[0] - 1)


def main():
    preds = yaml.safe_load(open(paths.PREDICTIONS_YAML, encoding="utf-8"))
    prices = pd.read_parquet(paths.PROCESSED / "prices.parquet")
    spcx, ndx = _series(prices, "SPCX"), _series(prices, "^NDX")
    today = pd.Timestamp(dt.date.today())
    days_since = (today - IPO_DATE).days
    last_close = float(spcx.iloc[-1]) if len(spcx) else None

    rows = []
    for p in preds["predictions"]:
        horizon_days = {"3 months": 91, "12 months": 365, "~180 days": 180, "1 month": 30}.get(
            p["horizon"], None)
        status, realized = "pending", None
        if horizon_days and days_since >= horizon_days and "vs_ndx" in p["id"]:
            r_spcx = _ret_over(spcx, IPO_DATE, horizon_days)
            r_ndx = _ret_over(ndx, IPO_DATE, horizon_days)
            if r_spcx is not None and r_ndx is not None:
                realized = round((r_spcx - r_ndx) * 100, 1)
                lo, hi = p["band_pct"]
                status = "within band" if lo <= realized <= hi else "outside band"
        rows.append({"id": p["id"], "horizon": p["horizon"], "point_pct": p["point_pct"],
                     "band_pct": p["band_pct"], "realized_pct": realized, "status": status})

    scorecard = {
        "updated": today.date().isoformat(),
        "days_since_ipo": int(days_since),
        "spcx_last_close": last_close,
        "spcx_vs_ipo_pct": round((last_close / preds["ipo_price"] - 1) * 100, 1) if last_close else None,
        "n_pending": sum(r["status"] == "pending" for r in rows),
        "rows": rows,
    }
    SCORECARD.write_text(json.dumps(scorecard, indent=2), encoding="utf-8")
    log(f"scorecard: day {days_since}, SPCX {scorecard['spcx_vs_ipo_pct']}% vs IPO, "
        f"{scorecard['n_pending']}/{len(rows)} pending")

    line = (f"- **{today.date()}** (day {days_since}): SPCX at "
            f"${last_close:.2f} ({scorecard['spcx_vs_ipo_pct']:+.1f}% vs $135 IPO). "
            + "; ".join(f"{r['id']} {r['status']}"
                        + (f" (realised {r['realized_pct']:+.1f}pp)" if r['realized_pct'] is not None else "")
                        for r in rows) + "\n")
    header = "# SPCX prediction tracker — changelog\n\n"
    existing = CHANGELOG.read_text(encoding="utf-8") if CHANGELOG.exists() else header
    # idempotent per date: drop any prior line for today before appending
    kept = [ln for ln in existing.splitlines(keepends=True)
            if not ln.startswith(f"- **{today.date()}**")]
    body = "".join(kept) if kept else header
    if not body.startswith("#"):
        body = header + body
    CHANGELOG.write_text(body + line, encoding="utf-8")
    log("updated changelog line (idempotent per date)")


if __name__ == "__main__":
    main()
