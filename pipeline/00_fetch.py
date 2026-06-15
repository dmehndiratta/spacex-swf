"""Stage 00 — fetch raw inputs into data/raw/<source>/<date>/, with validation and a
last-good fallback so a failed/empty pull never overwrites good data.

Sources (all keyless):
  - yfinance : SPCX + benchmarks + peers daily history
  - FRED     : CPIAUCSL monthly (CPI-U) via the keyless fredgraph CSV endpoint
  - comparables seed : copied through from data/seeds (version-controlled, not network)

Run:  python pipeline/00_fetch.py            (online)
      python pipeline/00_fetch.py --offline  (skip network, just validate last-good exists)
"""
from __future__ import annotations
import sys, io, json, argparse, datetime as dt
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import pandas as pd
import requests
from swf import paths, universe

TODAY = dt.date.today().isoformat()
FRED_CPI_URL = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=CPIAUCSL"


def log(msg: str) -> None:
    print(f"[00_fetch] {msg}", flush=True)


def _promote(source: str, name: str, df: pd.DataFrame, min_rows: int = 1) -> bool:
    """Validate then write a snapshot + update the 'latest' pointer. Returns success."""
    if df is None or len(df) < min_rows or df.dropna(how="all").empty:
        log(f"  ! {source}/{name}: validation failed ({0 if df is None else len(df)} rows) — keeping last-good")
        return False
    d = paths.raw_dir(source, TODAY)
    d.mkdir(parents=True, exist_ok=True)
    df.to_csv(d / f"{name}.csv", index=False)
    # latest pointer
    latest = paths.RAW / source / "latest"
    latest.mkdir(parents=True, exist_ok=True)
    df.to_csv(latest / f"{name}.csv", index=False)
    log(f"  ok {source}/{name}: {len(df)} rows -> {d.name}/ + latest/")
    return True


def _comparable_tickers() -> list[str]:
    """Comparable-set tickers (for the post-IPO drift dashboard) from the seed CSV."""
    try:
        seed = pd.read_csv(paths.DATA / "seeds" / "ipo_comparables.csv", comment="#")
        return [t for t in seed["yfinance_ticker"].dropna().unique().tolist()]
    except Exception:
        return []


def fetch_prices() -> None:
    import yfinance as yf
    import warnings; warnings.filterwarnings("ignore")
    frames = []
    tickers = list(dict.fromkeys(universe.ALL_LIVE + _comparable_tickers()))
    for tk in tickers:
        try:
            h = yf.Ticker(tk).history(period="max", auto_adjust=True)
            if h.empty:
                log(f"  - {tk}: no data"); continue
            s = h[["Close"]].reset_index()
            s.columns = ["date", "close"]
            s["date"] = pd.to_datetime(s["date"], utc=True).dt.tz_localize(None).dt.date
            s["ticker"] = tk
            frames.append(s[["date", "ticker", "close"]])
            log(f"  - {tk}: {len(s)} rows")
        except Exception as e:
            log(f"  ! {tk}: {type(e).__name__}: {e}")
    if frames:
        allp = pd.concat(frames, ignore_index=True)
        _promote("yfinance", "prices", allp, min_rows=10)


USASPENDING_URL = "https://api.usaspending.gov/api/v2/search/spending_by_award/"
USASPENDING_OVERTIME_URL = "https://api.usaspending.gov/api/v2/search/spending_over_time/"


def _overtime(agency: str | None) -> dict[str, float]:
    """SpaceX contract obligations by federal fiscal year (optionally filtered to one agency).
    Far more robust than per-award start dates, which USAspending often returns null."""
    flt = {"recipient_search_text": ["Space Exploration Technologies"],
           "award_type_codes": ["A", "B", "C", "D"],
           "time_period": [{"start_date": "2008-01-01", "end_date": "2026-09-30"}]}
    if agency:
        flt["agencies"] = [{"type": "awarding", "tier": "toptier", "name": agency}]
    r = requests.post(USASPENDING_OVERTIME_URL,
                      json={"group": "fiscal_year", "filters": flt}, timeout=45)
    r.raise_for_status()
    return {x["time_period"]["fiscal_year"]: (x["aggregated_amount"] or 0.0)
            for x in r.json().get("results", [])}


def fetch_usaspending_by_year() -> None:
    """Obligations by fiscal year, split NASA / DoD / other, for the timeline dashboard."""
    try:
        total = _overtime(None)
        nasa = _overtime("National Aeronautics and Space Administration")
        dod = _overtime("Department of Defense")
    except Exception as e:
        log(f"  ! usaspending over-time: {type(e).__name__}: {e} — keeping last-good")
        return
    rows = []
    for yr in sorted(total):
        n, d, t = nasa.get(yr, 0.0), dod.get(yr, 0.0), total.get(yr, 0.0)
        rows.append({"fiscal_year": int(yr), "nasa": n, "dod": d,
                     "other": max(t - n - d, 0.0), "total": t})
    _promote("usaspending", "spacex_by_year", pd.DataFrame(rows), min_rows=5)


def fetch_usaspending() -> None:
    """SpaceX federal awards (contracts + grants) from USAspending.gov (keyless).
    Pulls major awards paginated; aggregation happens in 10_clean. Honest caveat: this is the
    sum of identified major awards, not a guaranteed-exhaustive obligation total."""
    rows = []
    specs = [("contracts", ["A", "B", "C", "D"]), ("grants", ["02", "03", "04", "05"])]
    for kind, codes in specs:
        for page in range(1, 7):  # up to 600 awards/kind
            payload = {
                "filters": {"recipient_search_text": ["Space Exploration Technologies"],
                            "award_type_codes": codes,
                            "time_period": [{"start_date": "2008-01-01", "end_date": "2026-06-01"}]},
                "fields": ["Award ID", "Recipient Name", "Award Amount", "Awarding Agency",
                           "Period of Performance Start Date"],
                "limit": 100, "page": page, "sort": "Award Amount", "order": "desc",
            }
            try:
                r = requests.post(USASPENDING_URL, json=payload, timeout=45)
                r.raise_for_status()
                res = r.json().get("results", [])
            except Exception as e:
                log(f"  ! usaspending {kind} p{page}: {type(e).__name__}: {e}")
                break
            if not res:
                break
            for x in res:
                rows.append({"award_id": x.get("Award ID"), "kind": kind,
                             "amount": x.get("Award Amount") or 0,
                             "agency": x.get("Awarding Agency"),
                             "start": x.get("Period of Performance Start Date")})
            if len(res) < 100:
                break
    if rows:
        _promote("usaspending", "spacex_awards", pd.DataFrame(rows), min_rows=10)


def fetch_cpi() -> None:
    try:
        r = requests.get(FRED_CPI_URL, timeout=30)
        r.raise_for_status()
        df = pd.read_csv(io.StringIO(r.text))
        df.columns = ["date", "cpi"]
        df = df[df["cpi"] != "."]
        df["cpi"] = pd.to_numeric(df["cpi"], errors="coerce")
        df = df.dropna()
        _promote("fred", "cpi", df, min_rows=100)
    except Exception as e:
        log(f"  ! FRED CPI: {type(e).__name__}: {e} — keeping last-good")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--offline", action="store_true")
    args = ap.parse_args()
    paths.ensure_dirs()
    log(f"date={TODAY} offline={args.offline}")
    if args.offline:
        for src, name in (("yfinance", "prices"), ("fred", "cpi")):
            p = paths.RAW / src / "latest" / f"{name}.csv"
            log(f"  offline: {src}/{name} last-good {'present' if p.exists() else 'MISSING'}")
        return
    fetch_prices()
    fetch_cpi()
    fetch_usaspending()
    fetch_usaspending_by_year()
    # record a fetch manifest
    man = {"fetched_at": dt.datetime.now().isoformat(timespec="seconds"), "date": TODAY}
    (paths.RAW / "fetch_manifest.json").write_text(json.dumps(man, indent=2))
    log("done")


if __name__ == "__main__":
    main()
