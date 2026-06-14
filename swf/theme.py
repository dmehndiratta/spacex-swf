"""Burnside-Brutalist Plotly theme + a write_html() wrapper that emits dashboards
matching the existing site convention (CDN Plotly, IBM Plex fonts, paper background,
square corners, a mono header strip, and a footnote rule).

All dashboards in this project go through `figure_html()` or `page_html()` so the look
is consistent and theme-matched without copy-pasting CSS into 20 files.
"""
from __future__ import annotations
import plotly.graph_objects as go
import plotly.io as pio

# --- palette (mirrors src/styles/global.css) ---
VOID = "#0F0F0E"
SHADOW = "#353330"
CONCRETE = "#B2ADA8"
MIST = "#7A7671"
SURFACE = "#EDE9E3"
SIGNAL = "#C07B2F"
PAPER = "#FFFFFF"
PLOT_BG = "#EDE9E3"
GRID = "#E0DBD5"
BORDER = "#D4CFC9"
CTRL_BG = "#F5F2EE"

SANS = "IBM Plex Sans, system-ui, sans-serif"
MONO = "IBM Plex Mono, ui-monospace, monospace"

# Categorical sequence: signal orange leads, then earth tones — deliberately not rainbow.
CATEGORICAL = [SIGNAL, VOID, MIST, "#6B8E9E", "#8C6A4A", "#A8443B", "#5B7553", CONCRETE]
# Sequential (light paper -> signal) and diverging (loss red <-> gain green through paper).
SEQUENTIAL = [[0.0, "#F5F0E8"], [0.5, "#D9A86A"], [1.0, SIGNAL]]
DIVERGING = [[0.0, "#A8443B"], [0.5, SURFACE], [1.0, "#3F6B4F"]]

PLOTLY_CDN = "https://cdn.plot.ly/plotly-3.5.0.min.js"

_template = go.layout.Template()
_template.layout = go.Layout(
    font=dict(family=SANS, size=12, color=VOID),
    title=dict(font=dict(family=SANS, size=14, color=VOID), x=0, xref="paper", xanchor="left"),
    paper_bgcolor=PAPER,
    plot_bgcolor=PLOT_BG,
    colorway=CATEGORICAL,
    margin=dict(l=56, r=28, t=56, b=48),
    hovermode="closest",
    hoverlabel=dict(font=dict(family=MONO, size=11), bgcolor=VOID, font_color=SURFACE,
                    bordercolor=SIGNAL),
    xaxis=dict(gridcolor=GRID, linecolor=CONCRETE, zeroline=False, ticks="outside",
               tickcolor=CONCRETE, tickfont=dict(size=11, color=MIST, family=MONO),
               title=dict(font=dict(size=11, color=MIST, family=MONO))),
    yaxis=dict(gridcolor=GRID, linecolor=CONCRETE, zeroline=False, ticks="outside",
               tickcolor=CONCRETE, tickfont=dict(size=11, color=MIST, family=MONO),
               title=dict(font=dict(size=11, color=MIST, family=MONO))),
    legend=dict(font=dict(size=11, family=MONO, color=SHADOW), bgcolor="rgba(0,0,0,0)"),
    colorscale=dict(sequential=SEQUENTIAL, diverging=DIVERGING),
)
pio.templates["burnside"] = _template
pio.templates.default = "burnside"

CONFIG = {"responsive": True, "displayModeBar": False, "scrollZoom": False}


def style(fig: go.Figure, height: int | None = None) -> go.Figure:
    fig.update_layout(template="burnside", autosize=True)
    if height:
        fig.update_layout(height=height)
    return fig


# --- HTML page shell -------------------------------------------------------
_PAGE_CSS = f"""
*, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; border-radius: 0; }}
html, body {{ background: {PAPER}; font-family: {SANS}; color: {VOID};
  font-size: 13px; line-height: 1.5; }}
.dash-header {{ padding: 12px 16px 10px; border-bottom: 1px solid {BORDER}; background: {SURFACE}; }}
.dash-header h2 {{ font-size: 0.92rem; font-weight: 600; margin-bottom: 3px; }}
.dash-header p {{ font-size: 0.7rem; color: {MIST}; font-family: {MONO}; letter-spacing: 0.04em; }}
.controls {{ display: flex; flex-wrap: wrap; gap: 14px 22px; padding: 11px 16px;
  background: {CTRL_BG}; border-bottom: 1px solid {BORDER}; align-items: flex-end; }}
.ctrl-group {{ display: flex; flex-direction: column; gap: 5px; min-width: 0; }}
.ctrl-label {{ font-size: 0.6rem; font-weight: 600; letter-spacing: 0.1em; color: {MIST};
  text-transform: uppercase; font-family: {MONO}; }}
.ctrl-val {{ font-size: 0.72rem; color: {VOID}; font-family: {MONO}; font-weight: 500; }}
input[type=range] {{ width: 170px; accent-color: {SIGNAL}; }}
.pill-row {{ display: flex; gap: 6px; flex-wrap: wrap; }}
.pill {{ display: inline-flex; align-items: center; gap: 5px; padding: 3px 11px;
  border: 1px solid {CONCRETE}; cursor: pointer; font-size: 0.72rem; color: {VOID};
  background: {PAPER}; user-select: none; font-family: {MONO};
  transition: background .1s, color .1s, border-color .1s; }}
.pill input {{ display: none; }}
.pill.on {{ background: {VOID}; color: {SURFACE}; border-color: {VOID}; }}
.metrics {{ display: flex; flex-wrap: wrap; border-bottom: 1px solid {BORDER}; background: {PAPER}; }}
.metric {{ flex: 1; padding: 9px 14px; border-right: 1px solid {BORDER}; min-width: 120px; }}
.metric:last-child {{ border-right: none; }}
.metric-label {{ font-size: 0.58rem; text-transform: uppercase; letter-spacing: 0.09em;
  color: {MIST}; font-family: {MONO}; display: block; margin-bottom: 2px; }}
.metric-value {{ font-size: 1.05rem; font-weight: 600; color: {VOID}; display: block;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}
.metric-value.signal {{ color: {SIGNAL}; }}
.plot-wrap {{ width: 100%; }}
.footnote {{ padding: 7px 16px; font-size: 0.64rem; color: {MIST}; font-family: {MONO};
  border-top: 1px solid {BORDER}; background: {SURFACE}; }}
.footnote b {{ color: {SHADOW}; font-weight: 500; }}
a {{ color: {SIGNAL}; }}
"""


def figure_html(fig: go.Figure, title: str, subtitle: str, footnote: str,
                height: int = 460) -> str:
    """Wrap a single Plotly figure in the standard themed page shell."""
    import plotly.io as _pio
    style(fig, height=height)
    frag = _pio.to_html(fig, include_plotlyjs="cdn", full_html=False,
                        config=CONFIG, default_height=f"{height}px")
    return _shell(title, subtitle, body=f'<div class="plot-wrap">{frag}</div>',
                  footnote=footnote)


def page_html(title: str, subtitle: str, body: str, footnote: str,
              head_extra: str = "") -> str:
    """For interactive dashboards built with custom HTML controls + embedded JSON.
    `body` is raw HTML (controls + plot divs); plotly.js is loaded from CDN."""
    return _shell(title, subtitle, body=body, footnote=footnote,
                  head_extra=f'<script src="{PLOTLY_CDN}" crossorigin="anonymous"></script>{head_extra}')


def _shell(title: str, subtitle: str, body: str, footnote: str, head_extra: str = "") -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
{head_extra}
<style>{_PAGE_CSS}</style>
</head>
<body>
<div class="dash-header"><h2>{title}</h2><p>{subtitle}</p></div>
{body}
<div class="footnote">{footnote}</div>
</body>
</html>"""
