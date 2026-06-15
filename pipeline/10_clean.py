"""Stage 10 — normalise + join raw snapshots into data/processed/*.parquet.

Outputs:
  prices.parquet      long: date, ticker, close  (SPCX + benchmarks + peers)
  cpi.parquet         monthly CPI-U
  comparables.parquet seed facts + CPI-adjusted proceeds (2026 $) + computed fields
"""
from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import pandas as pd
from swf import paths


def log(m): print(f"[10_clean] {m}", flush=True)


def latest(source, name):
    return pd.read_csv(paths.RAW / source / "latest" / f"{name}.csv")


def main():
    paths.PROCESSED.mkdir(parents=True, exist_ok=True)

    # --- prices ---
    prices = latest("yfinance", "prices")
    prices["date"] = pd.to_datetime(prices["date"])
    prices = prices.dropna(subset=["close"]).sort_values(["ticker", "date"])
    prices.to_parquet(paths.PROCESSED / "prices.parquet", index=False)
    log(f"prices: {len(prices)} rows, {prices['ticker'].nunique()} tickers")

    # --- cpi ---
    cpi = latest("fred", "cpi")
    cpi["date"] = pd.to_datetime(cpi["date"])
    cpi = cpi.sort_values("date").reset_index(drop=True)
    cpi.to_parquet(paths.PROCESSED / "cpi.parquet", index=False)
    cpi_latest = float(cpi["cpi"].iloc[-1])
    log(f"cpi: {len(cpi)} rows, latest={cpi_latest:.1f} ({cpi['date'].iloc[-1].date()})")

    # --- comparables: CPI-adjust nominal proceeds to current dollars ---
    comp = pd.read_csv(paths.DATA / "seeds" / "ipo_comparables.csv", comment="#")
    comp["ipo_date"] = pd.to_datetime(comp["ipo_date"])

    def cpi_at(d):
        # nearest CPI month at or before the IPO date
        prior = cpi[cpi["date"] <= d]
        return float(prior["cpi"].iloc[-1]) if len(prior) else float(cpi["cpi"].iloc[0])

    comp["cpi_at_ipo"] = comp["ipo_date"].apply(cpi_at)
    comp["proceeds_real_bn"] = (comp["gross_proceeds_bn"] * cpi_latest / comp["cpi_at_ipo"]).round(2)
    comp["proceeds_with_greenshoe_bn"] = (comp["gross_proceeds_bn"] + comp["greenshoe_bn"]).round(2)
    comp["profitable_at_ipo"] = comp["profitable_at_ipo"].map({"Y": True, "N": False})
    comp["dual_class"] = comp["dual_class"].map({"Y": True, "N": False})
    comp = comp.sort_values("gross_proceeds_bn", ascending=False).reset_index(drop=True)
    comp.to_parquet(paths.PROCESSED / "comparables.parquet", index=False)
    log(f"comparables: {len(comp)} rows; CPI base={cpi_latest:.1f}; "
        f"largest real = {comp['proceeds_real_bn'].max():.1f}bn ({comp.iloc[0]['name']})")

    # --- USAspending: SpaceX federal awards -> by-year + by-agency aggregates ---
    aw_path = paths.RAW / "usaspending" / "latest" / "spacex_awards.csv"
    if aw_path.exists():
        aw = pd.read_csv(aw_path)
        aw["amount"] = pd.to_numeric(aw["amount"], errors="coerce").fillna(0)
        aw["year"] = pd.to_datetime(aw["start"], errors="coerce").dt.year
        aw["agency_short"] = aw["agency"].str.replace("National Aeronautics and Space Administration", "NASA", regex=False)
        aw["agency_short"] = aw["agency_short"].str.replace("Department of Defense", "DoD", regex=False)
        aw.to_parquet(paths.PROCESSED / "spacex_awards.parquet", index=False)
        total_bn = aw["amount"].sum() / 1e9
        log(f"spacex_awards: {len(aw)} awards, ${total_bn:.1f}B identified federal obligations")

    # --- USAspending: obligations by fiscal year (NASA / DoD / other) for the timeline ---
    by_path = paths.RAW / "usaspending" / "latest" / "spacex_by_year.csv"
    if by_path.exists():
        by = pd.read_csv(by_path)
        for c in ("nasa", "dod", "other", "total"):
            by[c] = pd.to_numeric(by[c], errors="coerce").fillna(0) / 1e9  # -> $bn
        by["fiscal_year"] = by["fiscal_year"].astype(int)
        by = by.sort_values("fiscal_year").reset_index(drop=True)
        by.to_parquet(paths.PROCESSED / "spacex_obligations_by_year.parquet", index=False)
        log(f"obligations_by_year: {len(by)} years, ${by['total'].sum():.1f}B total "
            f"({by['fiscal_year'].min()}-{by['fiscal_year'].max()})")

    log("done")


if __name__ == "__main__":
    main()
