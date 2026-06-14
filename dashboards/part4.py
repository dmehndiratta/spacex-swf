"""Part IV dashboards (plan.md §7 / §10 items 17-20)."""
from __future__ import annotations
import sys, json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import plotly.graph_objects as go
from swf import paths, theme

P4 = lambda: json.loads((paths.PROCESSED / "part4_models.json").read_text(encoding="utf-8"))
SRC4 = "Sources: Federal Reserve Distributional Financial Accounts (DFA) & SCF; Saez-Zucman / Realtime Inequality; Wyden Billionaires Income Tax; Treasury Greenbook. Figures illustrative — see SOURCES.md & methods."


# ---------------------------------------------------------------- 18. Unrealized gains by percentile
def d18_unrealized():
    g = P4()["unrealized"]
    b = g["buckets"]
    labels = [r["bucket"] for r in b]
    ur = [r["unrealized_t"] for r in b]
    other = [round(r["net_worth_t"] - r["unrealized_t"], 1) for r in b]
    fig = go.Figure()
    fig.add_bar(x=labels, y=other, name="Other net worth", marker_color=theme.CONCRETE,
                hovertemplate="%{x}<br>other: $%{y:.1f}T<extra></extra>")
    fig.add_bar(x=labels, y=ur, name="Unrealized capital gains", marker_color=theme.SIGNAL,
                hovertemplate="%{x}<br>unrealized gains: $%{y:.1f}T<extra></extra>")
    fig.update_layout(barmode="stack", legend=dict(orientation="h", y=1.1, x=0),
                      yaxis_title="Net worth ($T)", margin=dict(l=58, r=24, t=58, b=46))
    sub = (f"~${g['total_unrealized_t']:.0f}T of unrealized gains sit largely outside the income-tax base; "
           f"the top 1% holds ${g['top1_unrealized_t']:.0f}T ({g['top1_share_of_unrealized']*100:.0f}% of the total)")
    return "unrealized-gains.html", theme.figure_html(
        fig, "Wealth that the income tax never sees", sub, SRC4, height=440)


# ---------------------------------------------------------------- 17. Buy-borrow-die explainer
def d17_buy_borrow_die():
    bbd = P4()["buy_borrow_die"]
    data = {"start": bbd["start_value"], "ltcg": bbd["ltcg_rate"], "accrual": bbd["accrual_rate"]}
    body = f"""
<div class="controls">
  <div class="ctrl-group"><span class="ctrl-label">Annual appreciation</span>
    <input type="range" id="g" min="3" max="20" step="1" value="10"><span class="ctrl-val" id="gv">10%</span></div>
  <div class="ctrl-group"><span class="ctrl-label">Years held until death</span>
    <input type="range" id="y" min="5" max="40" step="1" value="20"><span class="ctrl-val" id="yv">20</span></div>
</div>
<div class="metrics">
  <div class="metric"><span class="metric-label">Gain over life</span><span class="metric-value" id="m-gain">—</span></div>
  <div class="metric"><span class="metric-label">Tax: buy-borrow-die</span><span class="metric-value signal" id="m-bbd">—</span></div>
  <div class="metric"><span class="metric-label">Tax: realize at death (no step-up)</span><span class="metric-value" id="m-real">—</span></div>
  <div class="metric"><span class="metric-label">Tax: annual accrual</span><span class="metric-value" id="m-acc">—</span></div>
</div>
<div class="plot-wrap"><div id="plot" style="height:340px"></div></div>
<div class="footnote" style="border-top:none">Per $1,000 invested. "Buy-borrow-die" = borrow against the appreciated asset, never sell,
and the heir's basis steps up at death (IRC §1014) — the gain is never taxed as income. Accrual taxes each year's gain.</div>
<script>
const DATA = {json.dumps(data)};
const SIGNAL="{theme.SIGNAL}", VOID="{theme.VOID}", MIST="{theme.MIST}", GRID="{theme.GRID}", CONCRETE="{theme.CONCRETE}";
function draw(){{
  const g=+document.getElementById('g').value/100, y=+document.getElementById('y').value;
  document.getElementById('gv').textContent=(g*100).toFixed(0)+'%'; document.getElementById('yv').textContent=y;
  const end=DATA.start*Math.pow(1+g,y), gain=end-DATA.start;
  let v=DATA.start, acc=0; for(let i=0;i<y;i++){{const yg=v*g; acc+=yg*DATA.accrual; v+=yg;}}
  const realTax=gain*DATA.ltcg;
  document.getElementById('m-gain').textContent='$'+gain.toFixed(0);
  document.getElementById('m-bbd').textContent='$0';
  document.getElementById('m-real').textContent='$'+realTax.toFixed(0);
  document.getElementById('m-acc').textContent='$'+acc.toFixed(0);
  Plotly.react('plot',[{{type:'bar', x:['Buy-borrow-die<br>(step-up)','Realize at death<br>(no step-up)','Annual accrual'],
    y:[0, realTax, acc], marker:{{color:[SIGNAL,CONCRETE,VOID]}}, text:['$0','$'+realTax.toFixed(0),'$'+acc.toFixed(0)],
    textposition:'auto', hovertemplate:'%{{x}}<br>$%{{y:.0f}} tax<extra></extra>'}}],
    {{font:{{family:'IBM Plex Sans'}}, paper_bgcolor:'#fff', plot_bgcolor:'#EDE9E3', margin:{{l:56,r:20,t:18,b:46}},
     yaxis:{{title:'Lifetime tax on the gain ($)', gridcolor:GRID}}, xaxis:{{gridcolor:GRID}}, showlegend:false}},
    {{responsive:true, displayModeBar:false}});
}}
['g','y'].forEach(id=>document.getElementById(id).addEventListener('input',draw)); draw();
</script>"""
    return "buy-borrow-die.html", theme.page_html(
        "Buy, borrow, die", "Why the largest fortunes can go untaxed — and what accrual would change",
        body, SRC4)


# ---------------------------------------------------------------- 19. Revenue simulator
def d19_revenue():
    p4 = P4()
    data = {"top01": p4["unrealized"]["top01_unrealized_t"], "top1": p4["unrealized"]["top1_unrealized_t"]}
    body = f"""
<div class="controls">
  <div class="ctrl-group"><span class="ctrl-label">Threshold tier</span>
    <div class="pill-row"><label class="pill on" id="p-1B"><input type="radio" name="thr" value="1B" checked> &gt;$1B net worth</label>
      <label class="pill" id="p-100M"><input type="radio" name="thr" value="100M"> &gt;$100M</label></div></div>
  <div class="ctrl-group"><span class="ctrl-label">Rate</span>
    <input type="range" id="rate" min="10" max="40" step="1" value="25"><span class="ctrl-val" id="rtv">25%</span></div>
  <div class="ctrl-group"><span class="ctrl-label">Expected return on the stock</span>
    <input type="range" id="ret" min="3" max="10" step="0.5" value="7"><span class="ctrl-val" id="rev">7.0%</span></div>
  <div class="ctrl-group"><span class="ctrl-label">Avoidance / migration</span>
    <input type="range" id="av" min="0" max="60" step="5" value="25"><span class="ctrl-val" id="avv">25%</span></div>
  <div class="ctrl-group"><span class="ctrl-label">Loss-refund drag (symmetry cost)</span>
    <input type="range" id="ld" min="0" max="40" step="5" value="15"><span class="ctrl-val" id="ldv">15%</span></div>
</div>
<div class="metrics">
  <div class="metric"><span class="metric-label">Taxable unrealized stock</span><span class="metric-value" id="m-base">—</span></div>
  <div class="metric"><span class="metric-label">Net revenue / year</span><span class="metric-value signal" id="m-rev">—</span></div>
  <div class="metric"><span class="metric-label">Over 10 years</span><span class="metric-value signal" id="m-10">—</span></div>
</div>
<div class="plot-wrap"><div id="plot" style="height:320px"></div></div>
<div class="footnote" style="border-top:none">Net revenue ≈ stock × expected return × rate × (1−avoidance) × (1−loss drag).
High-end estimates are sensitive to the avoidance elasticity — that uncertainty is the slider, not a hidden assumption.</div>
<script>
const DATA = {json.dumps(data)};
const SIGNAL="{theme.SIGNAL}", VOID="{theme.VOID}", GRID="{theme.GRID}";
function draw(){{
  const thr=document.querySelector('input[name=thr]:checked').value;
  const rate=+document.getElementById('rate').value/100, ret=+document.getElementById('ret').value/100,
    av=+document.getElementById('av').value/100, ld=+document.getElementById('ld').value/100;
  document.getElementById('p-1B').classList.toggle('on', thr==='1B');
  document.getElementById('p-100M').classList.toggle('on', thr==='100M');
  document.getElementById('rtv').textContent=(rate*100).toFixed(0)+'%';
  document.getElementById('rev').textContent=(ret*100).toFixed(1)+'%';
  document.getElementById('avv').textContent=(av*100).toFixed(0)+'%';
  document.getElementById('ldv').textContent=(ld*100).toFixed(0)+'%';
  const base = thr==='1B'? DATA.top01 : DATA.top1;
  const net = base*ret*rate*(1-av)*(1-ld)*1000; // $B
  document.getElementById('m-base').textContent='$'+base.toFixed(1)+'T';
  document.getElementById('m-rev').textContent='$'+net.toFixed(0)+'B';
  document.getElementById('m-10').textContent='$'+(net*10/1000).toFixed(2)+'T';
  // waterfall: gross -> after avoidance -> after loss drag
  const gross=base*ret*rate*1000, afterAv=gross*(1-av);
  Plotly.react('plot',[{{type:'bar', x:['Gross','After avoidance','Net (after loss refunds)'],
    y:[gross, afterAv, net], marker:{{color:[VOID,'#8C6A4A',SIGNAL]}},
    text:['$'+gross.toFixed(0)+'B','$'+afterAv.toFixed(0)+'B','$'+net.toFixed(0)+'B'], textposition:'auto',
    hovertemplate:'%{{x}}<br>$%{{y:.0f}}B/yr<extra></extra>'}}],
    {{font:{{family:'IBM Plex Sans'}}, paper_bgcolor:'#fff', plot_bgcolor:'#EDE9E3', margin:{{l:56,r:20,t:18,b:36}},
     yaxis:{{title:'$B / year', gridcolor:GRID}}, xaxis:{{gridcolor:GRID}}, showlegend:false}},
    {{responsive:true, displayModeBar:false}});
}}
document.querySelectorAll('input').forEach(el=>el.addEventListener('input',draw)); draw();
</script>"""
    return "tax-revenue.html", theme.page_html(
        "Accrual-tax revenue simulator", "What a mark-to-market tax on the very wealthy could raise",
        body, SRC4)


# ---------------------------------------------------------------- 20. Symmetry illustration
def d20_symmetry():
    s = P4()["symmetry"]
    rows = s["rows"]
    years = [f"Y{r['year']} ({r['return_pct']:+d}%)" for r in rows]
    fig = go.Figure()
    fig.add_bar(x=years, y=[r["tax_one_sided"] for r in rows], name="One-sided (gains only)",
                marker_color=theme.CONCRETE, hovertemplate="%{x}<br>tax $%{y:.1f}<extra></extra>")
    fig.add_bar(x=years, y=[r["tax_symmetric"] for r in rows], name="Symmetric (losses refunded)",
                marker_color=theme.SIGNAL, hovertemplate="%{x}<br>tax/refund $%{y:.1f}<extra></extra>")
    fig.add_hline(y=0, line=dict(color=theme.VOID, width=1))
    fig.update_layout(barmode="group", legend=dict(orientation="h", y=1.1, x=0),
                      yaxis_title="Tax paid (−refund) per $100", margin=dict(l=58, r=24, t=58, b=56))
    sub = (f"Over a volatile path the one-sided tax takes ${s['total_one_sided']:.0f} but the symmetric "
           f"tax takes only ${s['total_symmetric']:.0f} per $100 — symmetry is what makes accrual *fair*, not confiscatory")
    return "symmetry.html", theme.figure_html(
        fig, "Why symmetry matters", sub, SRC4, height=420)


STATIC_BUILDERS = [d18_unrealized, d20_symmetry]
INTERACTIVE_BUILDERS = [d17_buy_borrow_die, d19_revenue]
