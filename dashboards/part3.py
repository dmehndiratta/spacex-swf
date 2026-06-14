"""Part III dashboards (plan.md §6 / §10 items 13-16)."""
from __future__ import annotations
import sys, json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import pandas as pd
import plotly.graph_objects as go
from swf import paths, theme

P3 = lambda: json.loads((paths.PROCESSED / "part3_models.json").read_text(encoding="utf-8"))
SRC3 = "Sources: NBIM (GPFG), Alaska Permanent Fund Corp & PFD Division, Temasek/GIC, Australia Future Fund, Saudi PIF annual reports. Fund simulator calibrated to GPFG long-run real return. See SOURCES.md."


# ---------------------------------------------------------------- 13. SWF comparison
def d13_swf_comparison():
    df = pd.read_csv(paths.DATA / "seeds" / "swf_funds.csv", comment="#").sort_values("size_bn")
    colors = [theme.SIGNAL if "Alaska" in f else theme.VOID for f in df["fund"]]
    fig = go.Figure(go.Bar(
        y=df["fund"], x=df["size_bn"], orientation="h", marker_color=colors,
        customdata=df[["funding_source", "distribution_model", "governance_lesson"]].to_numpy(),
        text=[f"${v/1000:.2f}T" if v >= 1000 else f"${v:.0f}B" for v in df["size_bn"]],
        textposition="auto",
        hovertemplate="<b>%{y}</b><br>$%{x:.0f}B<br>Funding: %{customdata[0]}"
                      "<br>Distribution: %{customdata[1]}<br>Lesson: %{customdata[2]}<extra></extra>"))
    fig.update_layout(xaxis_title="Assets ($bn)", margin=dict(l=170, r=24, t=56, b=44))
    return "swf-comparison.html", theme.figure_html(
        fig, "The funds that already exist",
        "Sovereign & social wealth funds by assets — Alaska (the citizen-dividend model) in orange",
        SRC3, height=420)


# ---------------------------------------------------------------- 14. Fund simulator
def d14_fund_simulator():
    p3 = P3()
    data = {"us_adults": p3["us_adults"], "base": p3["fundsim_base"]["params"]}
    body = f"""
<div class="controls">
  <div class="ctrl-group"><span class="ctrl-label">Annual inflow (equity condition)</span>
    <input type="range" id="inflow" min="0" max="200" step="5" value="60"><span class="ctrl-val" id="iv">$60B/yr</span></div>
  <div class="ctrl-group"><span class="ctrl-label">Real return</span>
    <input type="range" id="ret" min="0" max="9" step="0.5" value="5"><span class="ctrl-val" id="rv">5.0%</span></div>
  <div class="ctrl-group"><span class="ctrl-label">Payout / dividend rule</span>
    <input type="range" id="pay" min="0" max="6" step="0.5" value="3"><span class="ctrl-val" id="pv">3.0%</span></div>
  <div class="ctrl-group"><span class="ctrl-label">Horizon</span>
    <input type="range" id="yrs" min="10" max="50" step="5" value="30"><span class="ctrl-val" id="yv">30 yrs</span></div>
  <div class="ctrl-group"><span class="ctrl-label">2008-style shock at yr 15</span>
    <label class="pill" id="shockpill"><input type="checkbox" id="shock"> stress</label></div>
</div>
<div class="metrics">
  <div class="metric"><span class="metric-label">Fund AUM (end)</span><span class="metric-value signal" id="m-aum">—</span></div>
  <div class="metric"><span class="metric-label">Annual payout (end)</span><span class="metric-value" id="m-pay">—</span></div>
  <div class="metric"><span class="metric-label">Citizen dividend (end)</span><span class="metric-value signal" id="m-div">—</span></div>
</div>
<div class="plot-wrap"><div id="plot" style="height:360px"></div></div>
<div class="footnote" style="border-top:none">AUM compounds at the real return, takes the annual inflow, pays out the rule,
and (optionally) takes a one-time drawdown at year 15. Dividend per ~{int(p3['us_adults']/1e6)}M US adults.
Calibrated to Norway's GPFG long-run return + spending rule.</div>
<script>
const DATA = {json.dumps(data)};
const SIGNAL="{theme.SIGNAL}", VOID="{theme.VOID}", MIST="{theme.MIST}", GRID="{theme.GRID}";
function sim(){{
  const inflow0=+document.getElementById('inflow').value, ret=+document.getElementById('ret').value/100,
    pay=+document.getElementById('pay').value/100, yrs=+document.getElementById('yrs').value,
    shock=document.getElementById('shock').checked;
  let aum=0, inflow=inflow0; const path=[];
  for(let y=1;y<=yrs;y++){{ aum*=(1+ret); if(shock&&y===15) aum*=0.65; aum+=inflow;
    const payout=aum*pay; aum-=payout; path.push({{y, aum, payout, div: payout*1e9/DATA.us_adults}}); inflow*=1.02; }}
  return path;
}}
function draw(){{
  document.getElementById('iv').textContent='$'+document.getElementById('inflow').value+'B/yr';
  document.getElementById('rv').textContent=(+document.getElementById('ret').value).toFixed(1)+'%';
  document.getElementById('pv').textContent=(+document.getElementById('pay').value).toFixed(1)+'%';
  document.getElementById('yv').textContent=document.getElementById('yrs').value+' yrs';
  document.getElementById('shockpill').classList.toggle('on', document.getElementById('shock').checked);
  const p=sim(), end=p[p.length-1];
  document.getElementById('m-aum').textContent='$'+(end.aum/1000).toFixed(2)+'T';
  document.getElementById('m-pay').textContent='$'+end.payout.toFixed(0)+'B';
  document.getElementById('m-div').textContent='$'+end.div.toFixed(0)+'/adult';
  Plotly.react('plot',[
    {{x:p.map(d=>d.y), y:p.map(d=>d.aum), name:'Fund AUM ($B)', mode:'lines', line:{{color:SIGNAL,width:2.5}},
      hovertemplate:'yr %{{x}}<br>AUM $%{{y:.0f}}B<extra></extra>'}},
    {{x:p.map(d=>d.y), y:p.map(d=>d.div), name:'Dividend/adult ($)', yaxis:'y2', mode:'lines',
      line:{{color:VOID,width:1.5,dash:'dot'}}, hovertemplate:'yr %{{x}}<br>$%{{y:.0f}}/adult<extra></extra>'}}
  ], {{font:{{family:'IBM Plex Sans'}}, paper_bgcolor:'#fff', plot_bgcolor:'#EDE9E3', margin:{{l:60,r:60,t:18,b:38}},
    legend:{{orientation:'h',y:1.12,x:0,font:{{size:10,family:'IBM Plex Mono'}}}},
    xaxis:{{title:'Year', gridcolor:GRID}}, yaxis:{{title:'AUM ($B)', gridcolor:GRID}},
    yaxis2:{{title:'$/adult', overlaying:'y', side:'right', showgrid:false}}}},
    {{responsive:true, displayModeBar:false}});
}}
['inflow','ret','pay','yrs','shock'].forEach(id=>document.getElementById(id).addEventListener('input',draw)); draw();
</script>"""
    return "fund-simulator.html", theme.page_html(
        "Social Wealth Fund growth simulator",
        "Equity-condition inflows → fund AUM and a universal citizen dividend",
        body, SRC3)


# ---------------------------------------------------------------- 15. Alaska PFD vs hypothetical
def d15_alaska_pfd():
    pfd = pd.read_csv(paths.DATA / "seeds" / "alaska_pfd.csv", comment="#")
    p3 = P3()
    hyp = p3["fundsim_base"]["end_dividend_per_capita"]
    fig = go.Figure()
    fig.add_bar(x=pfd["year"], y=pfd["pfd_usd"], marker_color=theme.CONCRETE, name="Alaska PFD (actual)",
                hovertemplate="%{x}: $%{y}<extra></extra>")
    fig.add_hline(y=hyp, line=dict(color=theme.SIGNAL, width=2, dash="dash"),
                  annotation_text=f"hypothetical US fund dividend ≈ ${hyp:.0f}/adult (30y base case)",
                  annotation_position="top left",
                  annotation_font=dict(family=theme.MONO, size=10, color=theme.SIGNAL))
    fig.update_layout(xaxis_title="Year", yaxis_title="Dividend per resident ($)",
                      margin=dict(l=58, r=24, t=56, b=44), showlegend=False)
    return "alaska-pfd.html", theme.figure_html(
        fig, "Alaska already does this",
        "The Alaska Permanent Fund Dividend, paid every year since 1982 — vs a modelled US fund dividend",
        SRC3, height=440)


# ---------------------------------------------------------------- 16. Precedent timeline
def d16_precedent():
    prec = P3()["precedents"]
    fig = go.Figure()
    for i, p in enumerate(prec):
        col = theme.SIGNAL if p["kept"] else theme.VOID
        y = 1 if i % 2 == 0 else -1
        fig.add_trace(go.Scatter(
            x=[p["year"]], y=[y], mode="markers+text", marker=dict(size=16, color=col, symbol="diamond"),
            text=[f"<b>{p['label']}</b>"], textposition="top center" if y > 0 else "bottom center",
            textfont=dict(family=theme.MONO, size=10, color=col),
            hovertemplate=f"{p['year']} — {p['label']}<br>{p['detail']}<extra></extra>", showlegend=False))
    fig.add_hline(y=0, line=dict(color=theme.CONCRETE, width=1))
    fig.update_layout(
        xaxis=dict(title="", range=[1969, 2037], gridcolor=theme.GRID),
        yaxis=dict(visible=False, range=[-2.2, 2.2]),
        margin=dict(l=24, r=24, t=40, b=30))
    return "precedent-timeline.html", theme.figure_html(
        fig, "Taking equity for public support is normal — keeping it is the novelty",
        "Chrysler warrants → TARP → UK bank stakes → the proposed standing condition (orange = retained)",
        SRC3, height=320)


STATIC_BUILDERS = [d13_swf_comparison, d15_alaska_pfd, d16_precedent]
INTERACTIVE_BUILDERS = [d14_fund_simulator]
