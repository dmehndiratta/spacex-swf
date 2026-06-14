# SpaceX IPO → Social Wealth Fund — analysis pipeline

The data + modelling engine behind the research page at
`/research/spacex-social-wealth-fund` on dhruv-mehndiratta.com.

It lives **inside** the Astro site repo (this folder) so the weekly GitHub Action can
regenerate data and dashboards, commit them, and let the existing Cloudflare Pages deploy
pick them up — the page is genuinely *living*, not a static snapshot.

## Layout
```
analysis/spacex-swf/
├── swf/                 # shared package: paths, facts loader, Plotly theme
├── data/
│   ├── facts/ipo_facts.yaml      # SINGLE SOURCE OF TRUTH for headline numbers
│   ├── predictions/predictions.yaml
│   ├── raw/<source>/<YYYY-MM-DD>/ # immutable dated snapshots (gitignored)
│   └── processed/*.parquet        # deterministic inputs to dashboards (committed)
├── pipeline/            # 00_fetch 10_clean 20_models 30_score 40_dashboards 50_facts
├── models/              # SOTP, reverse-DCF, TARP counterfactual, fund sim, revenue sim
├── run.py               # chains all stages
├── requirements.txt     # pinned, verified on Python 3.14
└── SOURCES.md           # every figure → a primary source
```
Dashboards are written to `../../public/research/spacex-social-wealth-fund/*.html`
(the site's static dir) and embedded in the MDX via the site's `IframeEmbed` component.

## Run it
```bash
cd analysis/spacex-swf
py -3.14 -m venv .venv
.venv/Scripts/python -m pip install -r requirements.txt
.venv/Scripts/python run.py            # full pipeline, fetch -> dashboards -> facts
.venv/Scripts/python run.py --stage 40 # one stage
.venv/Scripts/python run.py --offline  # skip network fetch, rebuild from last-good snapshots
```
Each stage is independently runnable and logs what it did. A failed fetch never overwrites
good data (validate-then-promote with a last-good fallback).

## Secrets
Keyless by default (USAspending, FCC, Treasury, Fed, Yahoo). The only optional key:
- `FRED_API_KEY` — free Federal Reserve key for macro series (CPI, rates). Without it the
  pipeline falls back to FRED's keyless CSV download endpoint.

In GitHub Actions, set these as repo **secrets** (none are required for a green pipeline run).

## Automation (the "living" refresh)
`.github/workflows/spacex-swf-update.yml` runs every **Monday 13:00 UTC** (and on manual
`workflow_dispatch`). It: installs deps → runs the full pipeline → builds the Astro site →
deploys to Cloudflare Pages → commits the refreshed `data/processed/`, `data/predictions/`,
`public/research/spacex-social-wealth-fund/`, and `src/data/spacex_facts.json` back to the repo.
Required secrets (reused from the existing deploy workflow): `CLOUDFLARE_API_TOKEN`,
`CLOUDFLARE_ACCOUNT_ID`. `FRED_API_KEY` is optional (keyless CSV fallback otherwise).
Fail-safe: a failed/empty fetch never overwrites good data — the pipeline falls back to the
last-good snapshot under `data/raw/<source>/latest/`.

## Pipeline stages
| stage | file | does |
|---|---|---|
| 00 | `00_fetch.py`     | pull each source → `data/raw/<source>/<date>/`, validate, promote |
| 10 | `10_clean.py`     | normalise + join → `data/processed/*.parquet` |
| 20 | `20_models.py`    | event studies, SOTP, reverse-DCF, TARP counterfactual, fund & revenue sims |
| 30 | `30_score.py`     | score frozen predictions vs realised SPCX → tracker + changelog |
| 40 | `40_dashboards.py`| regenerate every `*.html` dashboard from `data/processed` |
| 50 | `50_facts.py`     | regenerate injected facts JSON + "last updated" timestamp for the MDX |
