"""Interactive Part I dashboards: SOTP builder (4), risk heatmap (6), live tracker (8).
Self-contained: data embedded as JSON, rendered with CDN Plotly + vanilla JS."""
from __future__ import annotations
import sys, json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import pandas as pd
from swf import paths, theme

BUNDLE = lambda: json.loads((paths.PROCESSED / "part1_models.json").read_text(encoding="utf-8"))
SRC = "Sources: SpaceX S-1 & launch-week reporting; Yahoo Finance live tape. Multiples/scores are analyst assumptions — see SOURCES.md & the methods appendix."


# ---------------------------------------------------------------- 4. SOTP builder
def d4_sotp():
    b = BUNDLE()
    sotp = b["sotp"]
    data = {"segments": sotp["segments"], "market": b["facts"]["valuation_bn"]}
    body = f"""
<div class="controls" id="ctrls"></div>
<div class="metrics">
  <div class="metric"><span class="metric-label">Implied valuation (SOTP)</span>
    <span class="metric-value signal" id="m-total">—</span></div>
  <div class="metric"><span class="metric-label">Market mark</span>
    <span class="metric-value" id="m-mkt">—</span></div>
  <div class="metric"><span class="metric-label">Gap to market</span>
    <span class="metric-value" id="m-gap">—</span></div>
</div>
<div class="plot-wrap"><div id="plot" style="height:380px"></div></div>
<div class="footnote" style="border-top:none">Drag each segment's EV/forward-sales multiple. The bar
stacks segment values; the dashed line is the $1.77T market mark. Defaults are the base case.</div>
<script>
const DATA = {json.dumps(data)};
const SIGNAL="{theme.SIGNAL}", VOID="{theme.VOID}", MIST="{theme.MIST}", GRID="{theme.GRID}";
const keys = Object.keys(DATA.segments);
const state = {{}};
const ctrls = document.getElementById('ctrls');
keys.forEach(k => {{
  const s = DATA.segments[k];
  state[k] = s.mult.base;
  const g = document.createElement('div'); g.className='ctrl-group';
  g.innerHTML = `<span class="ctrl-label">${{s.label}}</span>
    <input type="range" min="${{s.mult.bear}}" max="${{s.mult.bull}}" step="0.5" value="${{s.mult.base}}" id="r-${{k}}">
    <span class="ctrl-val" id="v-${{k}}"></span>`;
  ctrls.appendChild(g);
  g.querySelector('input').addEventListener('input', e => {{ state[k]=+e.target.value; draw(); }});
}});
function fwd(s){{ return s.rev_bn*(1+s.growth); }}
function draw(){{
  let total=0; const x=[], y=[], txt=[];
  keys.forEach(k=>{{ const s=DATA.segments[k]; const ev=fwd(s)*state[k]; total+=ev;
    x.push(s.label.split(' ')[0]); y.push(ev); txt.push('$'+ev.toFixed(0)+'B<br>'+state[k].toFixed(1)+'x fwd sales');
    document.getElementById('v-'+k).textContent = state[k].toFixed(1)+'x  →  $'+ev.toFixed(0)+'B';
  }});
  const gap = (DATA.market-total)/DATA.market*100;
  document.getElementById('m-total').textContent='$'+(total/1000).toFixed(2)+'T';
  document.getElementById('m-mkt').textContent='$'+(DATA.market/1000).toFixed(2)+'T';
  document.getElementById('m-gap').textContent=(gap>=0?'−':'+')+Math.abs(gap).toFixed(0)+'% vs market';
  Plotly.react('plot', [{{type:'bar', x:x, y:y, marker:{{color:[SIGNAL,VOID,MIST]}},
      text:txt, hovertemplate:'%{{x}}<br>%{{text}}<extra></extra>', textposition:'none'}}],
    {{font:{{family:'IBM Plex Sans'}}, paper_bgcolor:'#fff', plot_bgcolor:'#EDE9E3',
      margin:{{l:56,r:24,t:20,b:36}}, yaxis:{{title:'Implied EV ($B)', gridcolor:GRID}},
      xaxis:{{gridcolor:GRID}}, showlegend:false,
      shapes:[{{type:'line', x0:-0.5, x1:keys.length-0.5, y0:DATA.market, y1:DATA.market,
        line:{{color:VOID, dash:'dash', width:1.5}}}}],
      annotations:[{{x:keys.length-0.5, y:DATA.market, text:'$1.77T market', showarrow:false,
        yshift:10, xanchor:'right', font:{{family:'IBM Plex Mono', size:10, color:VOID}}}}]}},
    {{responsive:true, displayModeBar:false}});
}}
draw();
</script>"""
    return "sotp-builder.html", theme.page_html(
        "Sum-of-the-parts builder", "Set each segment's multiple — see how far a defensible SOTP sits below the market mark",
        body, SRC)


# ---------------------------------------------------------------- 6. Risk heatmap
def d6_risk():
    rr = BUNDLE()["risk_register"]
    data = {"items": rr["items"], "categories": rr["categories"], "n": rr["n"]}
    body = f"""
<div class="controls"><div class="ctrl-group"><span class="ctrl-label">Filter category</span>
  <div class="pill-row" id="pills"></div></div></div>
<div class="metrics">
  <div class="metric"><span class="metric-label">Risks scored</span><span class="metric-value" id="m-n">—</span></div>
  <div class="metric"><span class="metric-label">Mean severity (of 25)</span><span class="metric-value" id="m-sev">—</span></div>
  <div class="metric"><span class="metric-label">Highest-severity risk</span><span class="metric-value signal" id="m-top" style="font-size:.8rem">—</span></div>
</div>
<div class="plot-wrap"><div id="plot" style="height:430px"></div></div>
<div class="footnote">How to read it: each dot is one risk. It sits further <b>right</b> the more likely it is, and
<b>higher up</b> the more damage it would do. The shaded background runs from calm (bottom-left) to dangerous
(top-right), so the risks that matter most are the big dots in the upper-right. Severity is just likelihood × impact,
from 1 to 25. The scores are our own judgement, not market data — the table below gives the reasoning for each.</div>
<table class="risk-table mono" id="risk-table">
  <thead><tr><th>Risk</th><th>Category</th><th class="num">L</th><th class="num">I</th><th class="num">Sev</th><th>Why we scored it this way</th></tr></thead>
  <tbody id="risk-rows"></tbody>
</table>
<style>
.risk-table {{ width:100%; border-collapse:collapse; font-size:0.7rem; margin-top:4px; }}
.risk-table th, .risk-table td {{ text-align:left; padding:5px 10px; border-bottom:1px solid {theme.BORDER}; vertical-align:top; }}
.risk-table th {{ color:{theme.MIST}; text-transform:uppercase; letter-spacing:0.06em; font-size:0.6rem; border-bottom:1px solid {theme.SHADOW}; }}
.risk-table td.num, .risk-table th.num {{ text-align:center; width:34px; }}
.risk-table .sev {{ font-weight:600; }}
.risk-table tr td:first-child {{ font-weight:600; color:{theme.VOID}; }}
.risk-table .note {{ color:{theme.MIST}; }}
</style>
<script>
const DATA = {json.dumps(data)};
const PALETTE = ["{theme.SIGNAL}","{theme.VOID}","{theme.MIST}","#6B8E9E","#8C6A4A","#A8443B","#5B7553"];
const SIGNAL="{theme.SIGNAL}", MIST="{theme.MIST}", GRID="{theme.GRID}";
const LIKE = ['','rare','unlikely','possible','likely','almost certain'];
const IMPACT = ['','minor','moderate','serious','severe','critical'];
const cats = DATA.categories; let active = new Set(cats);
const pills = document.getElementById('pills');
cats.forEach((c,i)=>{{ const l=document.createElement('label'); l.className='pill on';
  l.innerHTML=`<input type="checkbox" checked> ${{c}}`;
  l.querySelector('input').addEventListener('change', e=>{{ if(e.target.checked){{active.add(c);l.classList.add('on');}}else{{active.delete(c);l.classList.remove('on');}} draw(); }});
  pills.appendChild(l); }});
function jitter(v,i){{ return v + ((i%3)-1)*0.12; }}
function sevColor(s){{ return s>=16? '#A8443B' : s>=9? SIGNAL : '#5B7553'; }}
// background severity matrix (z = likelihood * impact), light wash so top-right reads "hot"
const gx=[1,2,3,4,5], gy=[1,2,3,4,5];
const gz = gy.map(j=>gx.map(i=>i*j));
function draw(){{
  const shown = DATA.items.filter(d=>active.has(d.category));
  document.getElementById('m-n').textContent = shown.length;
  document.getElementById('m-sev').textContent = shown.length? (shown.reduce((a,b)=>a+b.severity,0)/shown.length).toFixed(1):'—';
  document.getElementById('m-top').textContent = shown.length? shown.slice().sort((a,b)=>b.severity-a.severity)[0].risk:'—';
  const bg = {{type:'heatmap', x:gx, y:gy, z:gz, showscale:false, hoverinfo:'skip', opacity:0.28,
    colorscale:[[0,'#EDE9E3'],[0.45,'#E7C9A0'],[1,'#A8443B']], zsmooth:'best'}};
  const traces = [bg].concat(cats.filter(c=>active.has(c)).map((c)=>{{
    const items = shown.filter(d=>d.category===c);
    return {{x:items.map((d,i)=>jitter(d.likelihood,i)), y:items.map((d,i)=>jitter(d.impact,i)),
      mode:'markers', type:'scatter', name:c,
      marker:{{size:items.map(d=>11+d.severity*1.5), color:PALETTE[cats.indexOf(c)%PALETTE.length], opacity:0.9, line:{{color:'#fff',width:1.5}}}},
      text:items.map(d=>`<b>${{d.risk}}</b><br>${{d.category}}<br>likelihood ${{d.likelihood}}/5 (${{LIKE[d.likelihood]}}) × impact ${{d.impact}}/5 (${{IMPACT[d.impact]}}) = severity ${{d.severity}}<br><span style="font-size:10px">${{d.note}}</span>`),
      hovertemplate:'%{{text}}<extra></extra>'}};
  }}));
  Plotly.react('plot', traces, {{font:{{family:'IBM Plex Sans'}}, paper_bgcolor:'#fff', plot_bgcolor:'#EDE9E3',
    margin:{{l:96,r:24,t:24,b:64}}, legend:{{font:{{size:9, family:'IBM Plex Mono'}}, orientation:'h', y:-0.22}},
    xaxis:{{title:'How likely  →', range:[0.5,5.5], tickvals:[1,2,3,4,5], ticktext:LIKE.slice(1), gridcolor:GRID, tickfont:{{size:10}}}},
    yaxis:{{title:'How damaging  →', range:[0.5,5.5], tickvals:[1,2,3,4,5], ticktext:IMPACT.slice(1), gridcolor:GRID, tickfont:{{size:10}}}},
    annotations:[{{x:5,y:5,text:'most dangerous',showarrow:false,font:{{family:'IBM Plex Mono',size:9,color:'#A8443B'}},yshift:14}}]}},
    {{responsive:true, displayModeBar:false}});
  // table, sorted by severity
  const rows = shown.slice().sort((a,b)=>b.severity-a.severity).map(d=>
    `<tr><td>${{d.risk}}</td><td class="note">${{d.category}}</td><td class="num">${{d.likelihood}}</td>`+
    `<td class="num">${{d.impact}}</td><td class="num sev" style="color:${{sevColor(d.severity)}}">${{d.severity}}</td>`+
    `<td class="note">${{d.note}}</td></tr>`).join('');
  document.getElementById('risk-rows').innerHTML = rows;
}}
draw();
</script>"""
    return "risk-heatmap.html", theme.page_html(
        "What could go wrong, and how much it would matter",
        f"{rr['n']} risks, each scored on how likely it is and how much damage it would do",
        body, SRC)


# ---------------------------------------------------------------- 8. Live tracker
def d8_tracker():
    prices = pd.read_parquet(paths.PROCESSED / "prices.parquet")
    preds = __import__("yaml").safe_load(open(paths.PREDICTIONS_YAML, encoding="utf-8"))
    sc = json.loads((paths.PROCESSED / "scorecard.json").read_text(encoding="utf-8"))
    spcx = prices[prices["ticker"] == "SPCX"].sort_values("date")
    series = [{"date": str(d.date()), "close": round(float(c), 2)}
              for d, c in zip(spcx["date"], spcx["close"])]
    total_shares = round(1.77e12 / 135.0)
    fan = {k: round(v["ev_bn"] * 1e9 / total_shares, 1) for k, v in preds["scenario_fan"].items()}
    # x-range: from just before IPO to a sensible forward window (>= ~90 days), widening with data
    last_dt = pd.to_datetime(series[-1]["date"]) if series else pd.Timestamp("2026-06-12")
    xstart = "2026-06-10"
    xend = str((max(last_dt + pd.Timedelta(days=30), pd.Timestamp("2026-09-15"))).date())
    data = {"series": series, "ipo_price": preds["ipo_price"], "first_close": preds["first_day_close"],
            "fan": fan, "scorecard": sc, "predictions": preds["predictions"],
            "xrange": [xstart, xend]}
    rows = "".join(
        f"<tr><td>{p['horizon']}</td><td>{p['statement']}</td>"
        f"<td class='mono'>{p['point_pct']:+.0f}% [{p['band_pct'][0]:+.0f},{p['band_pct'][1]:+.0f}]</td>"
        f"<td class='mono' id='st-{p['id']}'>pending</td></tr>"
        for p in preds["predictions"])
    body = f"""
<div class="metrics">
  <div class="metric"><span class="metric-label">SPCX last</span><span class="metric-value signal" id="m-px">—</span></div>
  <div class="metric"><span class="metric-label">vs $135 IPO</span><span class="metric-value" id="m-vsipo">—</span></div>
  <div class="metric"><span class="metric-label">Days since IPO</span><span class="metric-value" id="m-days">—</span></div>
  <div class="metric"><span class="metric-label">Calls pending</span><span class="metric-value" id="m-pend">—</span></div>
</div>
<div class="plot-wrap"><div id="plot" style="height:360px"></div></div>
<div style="padding:8px 16px">
  <table style="width:100%; border-collapse:collapse; font-size:0.72rem" class="mono">
  <thead><tr style="text-align:left; color:{theme.MIST}; border-bottom:1px solid {theme.BORDER}">
    <th style="padding:4px 6px">Horizon</th><th>Prediction</th><th>Point [band]</th><th>Status</th></tr></thead>
  <tbody>{rows}</tbody></table>
</div>
<div class="footnote" style="border-top:none">Predictions frozen at publish; scored weekly by the pipeline.
Dotted lines = scenario-DCF fair value per share (enterprise value ÷ shares) — reference levels, not price forecasts.</div>
<script>
const DATA = {json.dumps(data)};
const SIGNAL="{theme.SIGNAL}", VOID="{theme.VOID}", MIST="{theme.MIST}", GRID="{theme.GRID}";
const sc = DATA.scorecard;
document.getElementById('m-px').textContent = sc.spcx_last_close? '$'+sc.spcx_last_close.toFixed(2):'—';
document.getElementById('m-vsipo').textContent = (sc.spcx_vs_ipo_pct>=0?'+':'')+sc.spcx_vs_ipo_pct+'%';
document.getElementById('m-days').textContent = sc.days_since_ipo;
document.getElementById('m-pend').textContent = sc.n_pending+' / '+sc.rows.length;
sc.rows.forEach(r=>{{ const el=document.getElementById('st-'+r.id); if(el){{ el.textContent=r.status+(r.realized_pct!=null?` (${{r.realized_pct>0?'+':''}}${{r.realized_pct}}pp)`:''); if(r.status==='outside band') el.style.color='#A8443B'; if(r.status==='within band') el.style.color='#5B7553'; }} }});
const dates = DATA.series.map(d=>d.date), px = DATA.series.map(d=>d.close);
const traces = [
  {{x:dates, y:px, mode:'lines+markers', name:'SPCX', line:{{color:SIGNAL,width:2.5}}, marker:{{size:7}},
    hovertemplate:'%{{x}}<br>$%{{y:.2f}}<extra></extra>'}},
];
// Scenario DCF fair-value-per-share, drawn as horizontal reference lines (NOT a price forecast).
const fanColors={{bull:'#5B7553', base:VOID, bear:'#A8443B'}};
const shapes=[{{type:'line', xref:'paper', x0:0,x1:1, y0:DATA.ipo_price, y1:DATA.ipo_price,
    line:{{color:MIST,dash:'dash',width:1}}}}];
const annos=[{{xref:'paper', x:0, y:DATA.ipo_price, text:'$135 IPO', showarrow:false, yshift:-9, xanchor:'left', font:{{family:'IBM Plex Mono',size:9,color:MIST}}}}];
Object.keys(DATA.fan).forEach(k=>{{
  shapes.push({{type:'line', xref:'paper', x0:0, x1:1, y0:DATA.fan[k], y1:DATA.fan[k],
    line:{{color:fanColors[k], dash:'dot', width:1.4}}}});
  annos.push({{xref:'paper', x:1, y:DATA.fan[k], text:k+' DCF $'+DATA.fan[k].toFixed(0), showarrow:false,
    xanchor:'right', yshift:8, font:{{family:'IBM Plex Mono',size:9,color:fanColors[k]}}}});
}});
Plotly.newPlot('plot', traces, {{font:{{family:'IBM Plex Sans'}}, paper_bgcolor:'#fff', plot_bgcolor:'#EDE9E3',
  margin:{{l:52,r:24,t:18,b:36}}, showlegend:false,
  yaxis:{{title:'Price / fair value per share ($)', gridcolor:GRID, rangemode:'tozero'}},
  xaxis:{{gridcolor:GRID, type:'date', range:DATA.xrange}}, shapes:shapes, annotations:annos}},
  {{responsive:true, displayModeBar:false}});
</script>"""
    return "tracker.html", theme.page_html(
        "Live SPCX tracker & prediction scorecard",
        f"Updated {sc['updated']} · day {sc['days_since_ipo']} · the 'living' part of the analysis",
        body, SRC)


INTERACTIVE_BUILDERS = [d4_sotp, d6_risk, d8_tracker]
