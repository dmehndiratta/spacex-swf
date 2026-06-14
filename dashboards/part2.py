"""Part II dashboards (plan.md §5 / §10 items 9-12)."""
from __future__ import annotations
import sys, json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import pandas as pd
import plotly.graph_objects as go
from swf import paths, theme

P2 = lambda: json.loads((paths.PROCESSED / "part2_models.json").read_text(encoding="utf-8"))
SRC2 = "Sources: USAspending.gov (SpaceX awards, identified major contracts); U.S. Treasury TARP reports & SIGTARP (illustrative, rounded); FCC RDOF orders; Good Jobs First. S&P 500 via Yahoo Finance. See SOURCES.md."


# ---------------------------------------------------------------- 9. Federal obligations timeline
def d9_obligations():
    aw = pd.read_parquet(paths.PROCESSED / "spacex_awards.parquet")
    aw = aw.dropna(subset=["year"])
    aw["year"] = aw["year"].astype(int)
    aw = aw[(aw["year"] >= 2008) & (aw["year"] <= 2026)]
    by = aw.groupby(["year", "agency_short"])["amount"].sum().reset_index()
    top = aw.groupby("agency_short")["amount"].sum().sort_values(ascending=False).head(4).index.tolist()
    by["agency_short"] = by["agency_short"].where(by["agency_short"].isin(top), "Other")
    pivot = by.groupby(["year", "agency_short"])["amount"].sum().unstack(fill_value=0) / 1e9
    fig = go.Figure()
    palette = {"NASA": theme.SIGNAL, "DoD": theme.VOID}
    for i, col in enumerate(pivot.columns):
        fig.add_bar(x=pivot.index, y=pivot[col], name=col,
                    marker_color=palette.get(col, theme.CATEGORICAL[(i + 2) % len(theme.CATEGORICAL)]),
                    hovertemplate=col + " %{x}: $%{y:.2f}B<extra></extra>")
    cum = pivot.sum(axis=1).cumsum()
    fig.add_trace(go.Scatter(x=cum.index, y=cum.values, name="Cumulative", yaxis="y2",
                             mode="lines+markers", line=dict(color=theme.SHADOW, width=2),
                             hovertemplate="cumulative %{x}: $%{y:.1f}B<extra></extra>"))
    fig.update_layout(barmode="stack", legend=dict(orientation="h", y=1.08, x=0),
                      xaxis_title="Award start year", yaxis_title="Obligations ($B/yr)",
                      yaxis2=dict(title="Cumulative ($B)", overlaying="y", side="right",
                                  showgrid=False, tickfont=dict(family=theme.MONO, size=10, color=theme.MIST)),
                      margin=dict(l=58, r=58, t=58, b=46))
    return "obligations-timeline.html", theme.figure_html(
        fig, "SpaceX's federal scaffolding, by year",
        "Identified NASA + DoD contract obligations (USAspending) — bars annual, line cumulative",
        SRC2, height=500)


# ---------------------------------------------------------------- 10. Support ledger
def d10_support():
    led = P2()["spacex_support"]
    items = led["items"]
    labels = [i["label"] for i in items]
    vals = [i["bn"] for i in items]
    colmap = {"contract": theme.VOID, "subsidy": theme.SIGNAL, "rescinded": theme.CONCRETE}
    colors = [colmap[i["kind"]] for i in items]
    fig = go.Figure(go.Bar(y=labels, x=vals, orientation="h", marker_color=colors,
                           text=[f"${v:.2f}B" for v in vals], textposition="auto",
                           hovertemplate="%{y}<br>$%{x:.2f}B<extra></extra>"))
    fig.update_layout(xaxis_title="$bn", margin=dict(l=240, r=24, t=56, b=44))
    sub = (f"Identified public support ≈ ${led['total_support_bn']}B in contracts + ${led['statelocal_received_m']:.0f}M "
           f"state/local; the FCC's ${led['rescinded_m']/1000:.2f}B RDOF award was rescinded (grey)")
    return "support-ledger.html", theme.figure_html(
        fig, "The public scaffolding ledger", sub, SRC2, height=360)


# ---------------------------------------------------------------- 11. Kept-it counterfactual
def d11_counterfactual():
    t = P2()["tarp"]
    data = {"rows": t["rows"], "totals": {k: t[k] for k in
            ("total_disbursed_bn", "total_realized_bn", "total_realized_pnl_bn",
             "total_kept_value_bn", "total_forfeited_bn")}, "as_of": t["as_of"]}
    body = f"""
<div class="controls">
  <div class="ctrl-group"><span class="ctrl-label">Market-return haircut on the "kept-it" sleeve</span>
    <input type="range" id="haircut" min="0" max="100" step="5" value="0">
    <span class="ctrl-val" id="hv">0% haircut · full market return</span></div>
</div>
<div class="metrics">
  <div class="metric"><span class="metric-label">Disbursed</span><span class="metric-value" id="m-disb">—</span></div>
  <div class="metric"><span class="metric-label">Actually realized</span><span class="metric-value" id="m-real">—</span></div>
  <div class="metric"><span class="metric-label">"Kept-it" value today</span><span class="metric-value signal" id="m-kept">—</span></div>
  <div class="metric"><span class="metric-label">Upside forfeited</span><span class="metric-value signal" id="m-forf">—</span></div>
</div>
<div class="plot-wrap"><div id="plot" style="height:380px"></div></div>
<div class="footnote" style="border-top:none">Each firm: what Treasury realized (sold 2009–2014) vs the same
proceeds reinvested in the S&P 500 to {data['as_of']}. Illustrative counterfactual, not a causal estimate;
price index understates total return. Drag the haircut to stress a lower market path.</div>
<script>
const DATA = {json.dumps(data)};
const SIGNAL="{theme.SIGNAL}", VOID="{theme.VOID}", MIST="{theme.MIST}", GRID="{theme.GRID}", CONCRETE="{theme.CONCRETE}";
function draw(){{
  const h = +document.getElementById('haircut').value/100;
  document.getElementById('hv').textContent = (h*100).toFixed(0)+'% haircut · '+((1-h)*100).toFixed(0)+'% of market return';
  const rows = DATA.rows;
  const names = rows.map(r=>r.program);
  const realized = rows.map(r=>r.realized_bn);
  const kept = rows.map(r=>r.realized_bn + (r.kept_value_bn-r.realized_bn)*(1-h));
  let tReal=0,tKept=0; rows.forEach((r,i)=>{{tReal+=realized[i];tKept+=kept[i];}});
  document.getElementById('m-disb').textContent='$'+DATA.totals.total_disbursed_bn.toFixed(0)+'B';
  document.getElementById('m-real').textContent='$'+tReal.toFixed(0)+'B';
  document.getElementById('m-kept').textContent='$'+(tKept/1000).toFixed(2)+'T';
  document.getElementById('m-forf').textContent='$'+((tKept-tReal)/1000).toFixed(2)+'T';
  Plotly.react('plot',[
    {{type:'bar', y:names, x:realized, orientation:'h', name:'Realized (sold)', marker:{{color:CONCRETE}},
      hovertemplate:'%{{y}}<br>realized $%{{x:.1f}}B<extra></extra>'}},
    {{type:'bar', y:names, x:kept.map((k,i)=>k-realized[i]), orientation:'h', name:'Forfeited upside',
      marker:{{color:SIGNAL}}, hovertemplate:'%{{y}}<br>forfeited $%{{x:.1f}}B<extra></extra>'}}
  ], {{barmode:'stack', font:{{family:'IBM Plex Sans'}}, paper_bgcolor:'#fff', plot_bgcolor:'#EDE9E3',
    margin:{{l:178,r:20,t:18,b:40}}, legend:{{orientation:'h',y:1.12,x:0,font:{{size:10,family:'IBM Plex Mono'}}}},
    xaxis:{{title:'$bn', gridcolor:GRID}}, yaxis:{{gridcolor:GRID, autorange:'reversed'}}}},
    {{responsive:true, displayModeBar:false}});
}}
document.getElementById('haircut').addEventListener('input', draw); draw();
</script>"""
    return "kept-it-counterfactual.html", theme.page_html(
        "What if the public had kept it?",
        "The 2008 bailout stakes: realized vs a retained market sleeve",
        body, SRC2)


# ---------------------------------------------------------------- 12. Equity-condition estimate
def d12_equity_condition():
    p2 = P2()
    ec = p2["equity_condition"]
    led = p2["spacex_support"]
    data = {"federal_bn": led["federal_contracts_bn"], "statelocal_bn": led["statelocal_received_m"]/1000,
            "subsidy_share": ec["subsidy_share"], "appreciation": ec["appreciation"]}
    body = f"""
<div class="controls">
  <div class="ctrl-group"><span class="ctrl-label">Equity stake rate on support</span>
    <input type="range" id="rate" min="0" max="30" step="1" value="10"><span class="ctrl-val" id="rv">10%</span></div>
  <div class="ctrl-group"><span class="ctrl-label">Contract share treated as subsidy-equivalent</span>
    <input type="range" id="ss" min="0" max="100" step="5" value="25"><span class="ctrl-val" id="ssv">25%</span></div>
  <div class="ctrl-group"><span class="ctrl-label">Valuation appreciation since support</span>
    <input type="range" id="appr" min="5" max="80" step="5" value="30"><span class="ctrl-val" id="av">30×</span></div>
</div>
<div class="metrics">
  <div class="metric"><span class="metric-label">Subsidy-equivalent support</span><span class="metric-value" id="m-base">—</span></div>
  <div class="metric"><span class="metric-label">Public stake today (SpaceX only)</span><span class="metric-value signal" id="m-stake">—</span></div>
  <div class="metric"><span class="metric-label">As a citizen dividend (÷332M)</span><span class="metric-value" id="m-div">—</span></div>
</div>
<div class="plot-wrap"><div id="plot" style="height:320px"></div></div>
<div class="footnote" style="border-top:none">Illustrative: stake today = (contracts×subsidy-share + state/local) × stake-rate × appreciation.
Contracts are payment for services — only the subsidy-equivalent slice is treated as convertible. SpaceX alone; the rule would apply economy-wide.</div>
<script>
const DATA = {json.dumps(data)};
const SIGNAL="{theme.SIGNAL}", VOID="{theme.VOID}", GRID="{theme.GRID}";
function draw(){{
  const rate=+document.getElementById('rate').value/100, ss=+document.getElementById('ss').value/100, appr=+document.getElementById('appr').value;
  document.getElementById('rv').textContent=(rate*100).toFixed(0)+'%';
  document.getElementById('ssv').textContent=(ss*100).toFixed(0)+'%';
  document.getElementById('av').textContent=appr+'×';
  const base = DATA.federal_bn*ss + DATA.statelocal_bn;
  const stake = base*rate*appr;
  document.getElementById('m-base').textContent='$'+base.toFixed(1)+'B';
  document.getElementById('m-stake').textContent='$'+stake.toFixed(1)+'B';
  document.getElementById('m-div').textContent='$'+(stake*1e9/332e6).toFixed(0)+'/person';
  Plotly.react('plot',[{{type:'bar', x:['Support (subsidy-equiv)','Public stake today'], y:[base, stake],
    marker:{{color:[VOID,SIGNAL]}}, text:['$'+base.toFixed(1)+'B','$'+stake.toFixed(1)+'B'], textposition:'auto',
    hovertemplate:'%{{x}}<br>$%{{y:.1f}}B<extra></extra>'}}],
    {{font:{{family:'IBM Plex Sans'}}, paper_bgcolor:'#fff', plot_bgcolor:'#EDE9E3', margin:{{l:56,r:20,t:18,b:36}},
     yaxis:{{title:'$bn', gridcolor:GRID}}, xaxis:{{gridcolor:GRID}}, showlegend:false}},
    {{responsive:true, displayModeBar:false}});
}}
['rate','ss','appr'].forEach(id=>document.getElementById(id).addEventListener('input',draw)); draw();
</script>"""
    return "equity-condition-estimate.html", theme.page_html(
        "The retroactive equity-condition estimate",
        "Had a warrant-priced equity condition attached to SpaceX's public support",
        body, SRC2)


STATIC_BUILDERS = [d9_obligations, d10_support]
INTERACTIVE_BUILDERS = [d11_counterfactual, d12_equity_condition]
