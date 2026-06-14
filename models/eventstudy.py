"""Event studies + first-day-pop distribution for Part I (plan.md §4.3, §4.6).

  - first_day_pop_stats() : locate SPCX's +19.2% in the mega-IPO distribution
  - peer_event_study()    : market-model abnormal returns + CARs for listed peers around
                            the SPCX debut (2026-06-12). HC-style: OLS alpha/beta on an
                            estimation window, AR = actual - (alpha + beta*mkt), CAR cumulated.
                            Living: thin now (one post-event session), fills in weekly.
"""
from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import numpy as np
import pandas as pd
from swf import paths, universe

EVENT_DATE = pd.Timestamp("2026-06-12")
EST_START, EST_END = -140, -16   # estimation window (trading days rel. to event)
EVT_START, EVT_END = -1, 20      # event window


def _load_prices() -> pd.DataFrame:
    return pd.read_parquet(paths.PROCESSED / "prices.parquet")


def first_day_pop_stats() -> dict:
    comp = pd.read_parquet(paths.PROCESSED / "comparables.parquet")
    pops = comp.dropna(subset=["first_day_return"]).copy()
    spcx = float(comp.loc[comp["ticker"] == "SPCX", "first_day_return"].iloc[0])
    others = pops.loc[pops["ticker"] != "SPCX", "first_day_return"]
    pct = float((others < spcx).mean() * 100)
    return {
        "spcx": spcx,
        "median": round(float(others.median()), 4),
        "mean": round(float(others.mean()), 4),
        "percentile": round(pct, 0),
        "n": int(others.shape[0]),
        "points": [
            {"name": r["name"], "ticker": r["ticker"], "ret": round(float(r["first_day_return"]), 4),
             "sector": r["sector"], "profitable": bool(r["profitable_at_ipo"])}
            for _, r in pops.sort_values("first_day_return").iterrows()
        ],
    }


def _daily_returns(prices: pd.DataFrame, ticker: str) -> pd.Series:
    s = prices[prices["ticker"] == ticker].sort_values("date").set_index("date")["close"]
    return s.pct_change().dropna()


def peer_event_study(market_ticker: str = "^NDX") -> dict:
    prices = _load_prices()
    mkt = _daily_returns(prices, market_ticker)
    # trading-day index relative to the event, built off the market calendar
    cal = mkt.index.to_list()
    if EVENT_DATE not in mkt.index:
        # event day may not yet be in the benchmark series alignment; use nearest >= event
        future = [d for d in cal if d >= EVENT_DATE]
        event_anchor = future[0] if future else cal[-1]
    else:
        event_anchor = EVENT_DATE
    anchor_i = cal.index(event_anchor)
    rel = {d: i - anchor_i for i, d in enumerate(cal)}

    results = []
    for tk in universe.EVENT_STUDY_PEERS:
        r = _daily_returns(prices, tk)
        joined = pd.concat([r.rename("ri"), mkt.rename("rm")], axis=1, sort=True).dropna()
        joined["rel"] = joined.index.map(rel)
        est = joined[(joined["rel"] >= EST_START) & (joined["rel"] <= EST_END)]
        evt = joined[(joined["rel"] >= EVT_START) & (joined["rel"] <= EVT_END)]
        if len(est) < 30 or evt.empty:
            continue
        # OLS market model
        X = np.column_stack([np.ones(len(est)), est["rm"].to_numpy()])
        y = est["ri"].to_numpy()
        beta, *_ = np.linalg.lstsq(X, y, rcond=None)
        alpha, b = beta
        resid = y - X @ beta
        sigma = float(np.std(resid, ddof=2))
        evt = evt.copy()
        evt["ar"] = evt["ri"] - (alpha + b * evt["rm"])
        car = float(evt["ar"].sum())
        n = len(evt)
        car_t = car / (sigma * np.sqrt(n)) if sigma > 0 and n else np.nan
        ar0 = evt.loc[evt["rel"] == 0, "ar"]
        results.append({
            "ticker": tk, "name": universe.PEER_NAMES.get(tk, tk),
            "beta": round(float(b), 2), "alpha_bps": round(float(alpha) * 1e4, 1),
            "car_pct": round(car * 100, 2), "car_t": round(float(car_t), 2),
            "n_event_days": int(n),
            "ar0_pct": round(float(ar0.iloc[0]) * 100, 2) if not ar0.empty else None,
        })
    results.sort(key=lambda d: d["car_pct"], reverse=True)
    return {
        "market": universe.BENCHMARKS.get(market_ticker, market_ticker),
        "event_date": str(EVENT_DATE.date()),
        "estimation_window": [EST_START, EST_END],
        "event_window": [EVT_START, EVT_END],
        "n_event_days_available": int(max((r["n_event_days"] for r in results), default=0)),
        "peers": results,
    }


if __name__ == "__main__":
    import json
    fp = first_day_pop_stats()
    print("first-day pop: SPCX", fp["spcx"], "median", fp["median"], "pctile", fp["percentile"])
    es = peer_event_study()
    print("event study peers:", len(es["peers"]), "post-event days:", es["n_event_days_available"])
    print(json.dumps(es["peers"][:3], indent=2))
