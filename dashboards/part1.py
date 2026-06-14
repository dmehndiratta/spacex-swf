"""Part I dashboards (plan.md §4 / §10 items 1-8). Each builder returns (filename, html).
Static figures go through theme.figure_html; interactive ones embed JSON + vanilla JS
into theme.page_html so they stay self-contained static files (CDN Plotly only)."""
from __future__ import annotations
import sys, json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from swf import paths, theme, universe

PRICES = lambda: pd.read_parquet(paths.PROCESSED / "prices.parquet")
COMP = lambda: pd.read_parquet(paths.PROCESSED / "comparables.parquet")
BUNDLE = lambda: json.loads((paths.PROCESSED / "part1_models.json").read_text(encoding="utf-8"))
SRC = "Sources: SpaceX S-1 & launch-week reporting (CNBC, Morningstar, Via Satellite); FRED CPI-U; Yahoo Finance. See SOURCES.md."


# ---------------------------------------------------------------- 1. League table
def d1_league_table():
    comp = COMP().sort_values("proceeds_real_bn")
    names = comp["name"].tolist()
    colors = [theme.SIGNAL if t == "SPCX" else theme.CONCRETE for t in comp["ticker"]]
    colors_real = [theme.SIGNAL if t == "SPCX" else theme.MIST for t in comp["ticker"]]
    fig = go.Figure()
    fig.add_bar(y=names, x=comp["gross_proceeds_bn"], orientation="h", name="Nominal $bn",
                marker_color=colors, opacity=0.55,
                hovertemplate="%{y}<br>Nominal: $%{x:.1f}B<extra></extra>")
    fig.add_bar(y=names, x=comp["proceeds_real_bn"], orientation="h", name="2026 $bn (CPI-adj)",
                marker_color=colors_real,
                hovertemplate="%{y}<br>Real (2026$): $%{x:.1f}B<extra></extra>")
    fig.update_layout(barmode="overlay", legend=dict(orientation="h", y=1.06, x=0),
                      xaxis_title="Gross proceeds ($bn)", margin=dict(l=130, r=24, t=60, b=46))
    return "league-table.html", theme.figure_html(
        fig, "The largest IPO in history, in real terms",
        "Gross proceeds, nominal vs CPI-adjusted to 2026 dollars — SPCX in signal orange",
        SRC, height=560)


# ---------------------------------------------------------------- 2. First-day pop
def d2_first_day_pop():
    fp = BUNDLE()["first_day_pop"]
    pts = sorted(fp["points"], key=lambda d: d["ret"])
    names = [p["name"] for p in pts]
    rets = [p["ret"] * 100 for p in pts]
    colors = [theme.SIGNAL if p["ticker"] == "SPCX" else
              (theme.VOID if p["profitable"] else theme.MIST) for p in pts]
    fig = go.Figure()
    fig.add_bar(y=names, x=rets, orientation="h", marker_color=colors,
                hovertemplate="%{y}<br>First-day: %{x:.1f}%<extra></extra>")
    fig.add_vline(x=fp["median"] * 100, line=dict(color=theme.SHADOW, dash="dot", width=1),
                  annotation_text=f"median {fp['median']*100:.0f}%", annotation_position="top")
    fig.update_layout(xaxis_title="First-day return vs IPO price (%)",
                      margin=dict(l=130, r=24, t=60, b=46))
    sub = (f"SPCX +{fp['spcx']*100:.1f}% sits at the {fp['percentile']:.0f}th percentile of "
           f"{fp['n']} mega-IPOs — dark = profitable at IPO, grey = loss-making")
    return "first-day-pop.html", theme.figure_html(
        fig, "A middling pop for the biggest deal ever", sub, SRC, height=560)


# ---------------------------------------------------------------- 3. Post-IPO drift
def d3_drift():
    comp = COMP()
    prices = PRICES()
    fig = go.Figure()
    MAXD = 756  # ~3 trading years
    medians = []
    for _, r in comp.iterrows():
        tk = r["yfinance_ticker"]
        if not isinstance(tk, str):
            continue
        s = prices[(prices["ticker"] == tk) & (prices["date"] >= r["ipo_date"])].sort_values("date")
        if len(s) < 5:
            continue
        cum = (s["close"].to_numpy() / s["close"].to_numpy()[0] - 1) * 100
        d = np.arange(len(cum))
        m = d <= MAXD
        is_spcx = r["ticker"] == "SPCX"
        fig.add_trace(go.Scatter(
            x=d[m], y=cum[m], mode="lines+markers" if is_spcx else "lines",
            name=r["name"], legendgroup=r["name"],
            line=dict(color=theme.SIGNAL if is_spcx else theme.CONCRETE,
                      width=3 if is_spcx else 1.2),
            opacity=1.0 if is_spcx else 0.55,
            hovertemplate=r["name"] + "<br>day %{x}: %{y:.0f}%<extra></extra>"))
    fig.add_hline(y=0, line=dict(color=theme.SHADOW, width=1))
    fig.update_layout(xaxis_title="Trading days since IPO",
                      yaxis_title="Cumulative total return (%)",
                      legend=dict(font=dict(size=9)), margin=dict(l=60, r=24, t=60, b=46))
    return "post-ipo-drift.html", theme.figure_html(
        fig, "Post-IPO drift, in event time",
        "Cumulative return from the IPO price, aligned at t=0 — the mega-IPO base rate is unkind; "
        "SPCX (orange) has one session so far and grows weekly",
        SRC, height=560)


# ---------------------------------------------------------------- 5. Reverse-DCF grid
def d5_reverse_dcf():
    rd = BUNDLE()["reverse_dcf"]
    z = rd["implied_cagr_pct"]
    x = [f"{w:.0f}%" for w in rd["waccs"]]
    y = [f"{m}%" for m in rd["margins"]]
    fig = go.Figure(go.Heatmap(
        z=z, x=x, y=y, colorscale=theme.SEQUENTIAL, colorbar=dict(title="Implied<br>rev CAGR %"),
        text=[[f"{v:.0f}%" for v in row] for row in z], texttemplate="%{text}",
        textfont=dict(family=theme.MONO, size=12),
        hovertemplate="WACC %{x}, steady margin %{y}<br>implies %{z:.0f}% revenue CAGR<extra></extra>"))
    fig.update_layout(xaxis_title="Discount rate (WACC)",
                      yaxis_title="Steady-state FCF margin",
                      margin=dict(l=80, r=24, t=64, b=46))
    bc = rd["base_case"]
    sub = (f"To justify the $1.77T valuation you must believe ~{bc['implied_cagr_pct']:.0f}% revenue "
           f"growth for 10 years (base: {int(bc['ss_margin']*100)}% margin, {int(bc['wacc']*100)}% WACC)")
    return "reverse-dcf.html", theme.figure_html(
        fig, "What you must believe", sub, SRC, height=460)


# ---------------------------------------------------------------- 7. Lockup + index flows
def d7_lockup_flows():
    b = BUNDLE()
    lw, ix = b["lockup"], b["index_inclusion"]
    days = [t["day"] for t in lw["tranches"]]
    vals = [t["value_bn"] for t in lw["tranches"]]
    labels = [t["label"] for t in lw["tranches"]]
    absorb = [t["days_to_absorb"] for t in lw["tranches"]]
    fig = go.Figure()
    fig.add_bar(x=days, y=vals, marker_color=theme.SIGNAL, width=14,
                customdata=np.array([labels, absorb], dtype=object).T,
                hovertemplate="%{customdata[0]}<br>day %{x}<br>$%{y:.0f}B unlocked"
                              "<br>%{customdata[1]} ADV-days to absorb<extra></extra>",
                name="Lockup supply ($B)")
    # index passive demand markers
    for i in ix["indices"]:
        if i["gate_passed"]:
            fig.add_trace(go.Scatter(
                x=[60], y=[i["passive_demand_bn"]], mode="markers+text",
                marker=dict(color=theme.VOID, size=14, symbol="diamond"),
                text=[f"  {i['index']} passive demand ${i['passive_demand_bn']:.0f}B"],
                textposition="middle right", textfont=dict(family=theme.MONO, size=10),
                name=i["index"], hovertemplate=f"{i['index']}: +${i['passive_demand_bn']:.0f}B "
                f"(weight {i['target_weight_pct']:.2f}%)<extra></extra>"))
    fig.update_layout(xaxis_title="Days after IPO", yaxis_title="$bn",
                      showlegend=False, margin=dict(l=64, r=24, t=64, b=46))
    sub = (f"Free float is only {lw['float_pct_of_total']:.1f}% of shares; staged unlocks add "
           f"hundreds of $bn of supply against ~{lw['adv_shares']/1e6:.0f}M ADV. Diamond = index inflow.")
    return "lockup-flows.html", theme.figure_html(
        fig, "Supply waterfall vs index demand", sub, SRC, height=480)


STATIC_BUILDERS = [d1_league_table, d2_first_day_pop, d3_drift, d5_reverse_dcf, d7_lockup_flows]
