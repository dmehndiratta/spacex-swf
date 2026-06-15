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
    END = 2030  # right edge; the "perpetuity" bar runs to here and then arrows onward
    fig = go.Figure()
    labels = [p["label"] for p in prec]
    # one horizontal bar per precedent: from the year equity was taken to the year it was sold
    for i, p in enumerate(prec):
        kept = p["kept"]
        sold = p["sold"] if p["sold"] is not None else END
        color = theme.SIGNAL if kept else theme.SHADOW
        span = sold - p["taken"]
        fig.add_trace(go.Scatter(
            x=[p["taken"], sold], y=[i, i], mode="lines",
            line=dict(color=color, width=14),
            hovertemplate=f"<b>{p['label']}</b><br>{p['equity']}<br>{p['outcome']}<extra></extra>",
            showlegend=False))
        # marker + year where the stake was taken
        fig.add_trace(go.Scatter(
            x=[p["taken"]], y=[i], mode="markers+text", marker=dict(size=9, color=color),
            text=[f" {p['taken']}"], textposition="middle left",
            textfont=dict(family=theme.MONO, size=10, color=theme.MIST), showlegend=False,
            hoverinfo="skip"))
        if p["sold"] is not None:
            # "sold back" marker + year
            fig.add_trace(go.Scatter(
                x=[sold], y=[i], mode="markers+text", marker=dict(size=9, color=color, symbol="x"),
                text=[f"sold {p['sold']} "], textposition="middle right",
                textfont=dict(family=theme.MONO, size=10, color=theme.MIST), showlegend=False,
                hoverinfo="skip"))
        else:
            # perpetuity arrow + label
            fig.add_annotation(x=END, y=i, ax=END - 1.4, ay=i, xref="x", yref="y",
                               axref="x", ayref="y", showarrow=True, arrowhead=2,
                               arrowsize=1.1, arrowwidth=3, arrowcolor=theme.SIGNAL)
            fig.add_annotation(x=END, y=i, text="held in perpetuity →", showarrow=False,
                               xanchor="right", yshift=16,
                               font=dict(family=theme.MONO, size=10, color=theme.SIGNAL))
    fig.update_layout(
        xaxis=dict(title="", range=[1975, 2031], dtick=10, gridcolor=theme.GRID),
        yaxis=dict(tickvals=list(range(len(prec))), ticktext=labels,
                   range=[-0.7, len(prec) - 0.3], autorange=False,
                   tickfont=dict(family=theme.MONO, size=11, color=theme.VOID)),
        margin=dict(l=210, r=30, t=40, b=34))
    return "precedent-timeline.html", theme.figure_html(
        fig, "Every time the public took equity, it sold back",
        "How long each public equity stake was held. Grey bars were sold off within years; "
        "the proposed condition (orange) is the first designed to be kept.",
        SRC3, height=340)


# ---------------------------------------------------------------- 17. Economy-wide portfolio
def d17_economy_wide():
    p3 = P3()
    ew = p3["economy_wide"]
    data = {"companies": ew["companies"], "by_sector": ew["by_sector"],
            "total_subsidy_bn": ew["total_subsidy_bn"], "n_companies": ew["n_companies"],
            "n_sectors": ew["n_sectors"], "us_adults": p3["us_adults"]}
    body = f"""
<div class="controls">
  <div class="ctrl-group"><span class="ctrl-label">Stake value today (multiple of original subsidy)</span>
    <input type="range" id="mult" min="1" max="6" step="0.5" value="3"><span class="ctrl-val" id="mv">3.0×</span></div>
  <div class="ctrl-group"><span class="ctrl-label">Share routed to company employees</span>
    <input type="range" id="emp" min="0" max="100" step="5" value="40"><span class="ctrl-val" id="ev">40%</span></div>
  <div class="ctrl-group"><span class="ctrl-label">Fund payout / dividend rule</span>
    <input type="range" id="pay" min="1" max="5" step="0.5" value="3"><span class="ctrl-val" id="pv">3.0%</span></div>
</div>
<div class="metrics">
  <div class="metric"><span class="metric-label">Identified subsidies</span><span class="metric-value" id="m-sub">—</span></div>
  <div class="metric"><span class="metric-label">Portfolio value today</span><span class="metric-value signal" id="m-port">—</span></div>
  <div class="metric"><span class="metric-label">To the fund</span><span class="metric-value" id="m-fund">—</span></div>
  <div class="metric"><span class="metric-label">To employees</span><span class="metric-value" id="m-emp">—</span></div>
  <div class="metric"><span class="metric-label">Citizen dividend</span><span class="metric-value signal" id="m-div">—</span></div>
</div>
<div class="plot-wrap"><div id="psector" style="height:300px"></div></div>
<div class="plot-wrap"><div id="pcompany" style="height:420px"></div></div>
<div class="footnote" style="border-top:none">Curated, illustrative set of {data['n_companies']} large US-listed
subsidy recipients across {data['n_sectors']} sectors (Good Jobs First and public reporting; bailouts excluded).
"Stake value today" folds the stake rate and post-support appreciation into one multiple on the original subsidy.
Hover a company to see the implied stake as a share of its market cap; where that share is large, routing part of it
to employees keeps the firm fundable while still spreading ownership.</div>
<script>
const DATA = {json.dumps(data)};
const SIGNAL="{theme.SIGNAL}", VOID="{theme.VOID}", MIST="{theme.MIST}", GRID="{theme.GRID}", CONCRETE="{theme.CONCRETE}";
const PALETTE = {json.dumps(theme.CATEGORICAL)};
const sectors = DATA.by_sector.map(s=>s.sector);
const sectorColor = {{}}; sectors.forEach((s,i)=>sectorColor[s]=PALETTE[i % PALETTE.length]);
function fmt(bn){{ return bn>=1000 ? '$'+(bn/1000).toFixed(2)+'T' : '$'+bn.toFixed(0)+'B'; }}
function draw(){{
  const m=+document.getElementById('mult').value, e=+document.getElementById('emp').value/100,
        p=+document.getElementById('pay').value/100;
  document.getElementById('mv').textContent=m.toFixed(1)+'×';
  document.getElementById('ev').textContent=(e*100).toFixed(0)+'%';
  document.getElementById('pv').textContent=(p*100).toFixed(1)+'%';
  const port = DATA.total_subsidy_bn * m;
  const fund = port*(1-e), emp = port*e;
  document.getElementById('m-sub').textContent=fmt(DATA.total_subsidy_bn);
  document.getElementById('m-port').textContent=fmt(port);
  document.getElementById('m-fund').textContent=fmt(fund);
  document.getElementById('m-emp').textContent=fmt(emp);
  document.getElementById('m-div').textContent='$'+(fund*1e9*p/DATA.us_adults).toFixed(0)+'/adult';
  // sector chart (portfolio value by sector = subsidy_by_sector * m)
  const secVals = DATA.by_sector.map(s=>s.subsidy_bn*m);
  Plotly.react('psector',[{{type:'bar', x:secVals, y:sectors, orientation:'h',
    marker:{{color:sectors.map(s=>sectorColor[s])}},
    text:secVals.map(v=>fmt(v)), textposition:'auto',
    hovertemplate:'%{{y}}<br>portfolio value '+'%{{text}}<extra></extra>'}}],
    {{font:{{family:'IBM Plex Sans'}}, paper_bgcolor:'#fff', plot_bgcolor:'#EDE9E3',
     margin:{{l:140,r:20,t:30,b:34}}, title:{{text:'Diversified across sectors',font:{{size:12,family:'IBM Plex Mono',color:MIST}},x:0}},
     xaxis:{{title:'$B', gridcolor:GRID}}, yaxis:{{autorange:'reversed', gridcolor:GRID}}, showlegend:false}},
    {{responsive:true, displayModeBar:false}});
  // per-company chart (stake value), hover shows % of market cap
  const cs = DATA.companies;
  const names = cs.map(c=>c.company);
  const stake = cs.map(c=>c.subsidy_bn*m);
  const pct = cs.map(c=>100*c.subsidy_bn*m/c.market_cap_bn);
  Plotly.react('pcompany',[{{type:'bar', x:stake, y:names, orientation:'h',
    marker:{{color:cs.map(c=>sectorColor[c.sector])}},
    customdata:cs.map((c,i)=>[c.sector, pct[i], c.subsidy_bn]),
    hovertemplate:'<b>%{{y}}</b> (%{{customdata[0]}})<br>subsidy $%{{customdata[2]:.1f}}B → stake '+'%{{x:.1f}}B'+
      '<br>≈ %{{customdata[1]:.0f}}% of market cap<extra></extra>'}}],
    {{font:{{family:'IBM Plex Sans'}}, paper_bgcolor:'#fff', plot_bgcolor:'#EDE9E3',
     margin:{{l:140,r:20,t:30,b:36}}, title:{{text:'By company (stake value today)',font:{{size:12,family:'IBM Plex Mono',color:MIST}},x:0}},
     xaxis:{{title:'$B', gridcolor:GRID}}, yaxis:{{autorange:'reversed', gridcolor:GRID, tickfont:{{size:10}}}}, showlegend:false}},
    {{responsive:true, displayModeBar:false}});
}}
['mult','emp','pay'].forEach(id=>document.getElementById(id).addEventListener('input',draw)); draw();
</script>"""
    return "economy-wide-portfolio.html", theme.page_html(
        "The portfolio, extended across the economy",
        "Every major US-listed company that took subsidies or tax breaks — one diversified public stake",
        body, SRC3)


STATIC_BUILDERS = [d13_swf_comparison, d15_alaska_pfd, d16_precedent]
INTERACTIVE_BUILDERS = [d14_fund_simulator, d17_economy_wide]
