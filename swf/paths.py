"""Canonical paths. Resolves the pipeline root and the Astro site root separately
so the pipeline can live anywhere and still write outputs into the Website repo."""
from __future__ import annotations
from pathlib import Path
import datetime as _dt

ROOT = Path(__file__).resolve().parents[1]  # d:\Python Projects\SpaceX + SWF

DATA = ROOT / "data"
FACTS = DATA / "facts"
PREDICTIONS = DATA / "predictions"
RAW = DATA / "raw"
PROCESSED = DATA / "processed"

PIPELINE = ROOT / "pipeline"
MODELS = ROOT / "models"

# ── Astro site root ──────────────────────────────────────────────────────────
# Read from config.toml if present, else auto-detect a sibling Website folder.
def _resolve_site_root() -> Path:
    cfg = ROOT / "config.toml"
    if cfg.exists():
        for line in cfg.read_text(encoding="utf-8").splitlines():
            if line.strip().startswith("website_root"):
                val = line.split("=", 1)[1].strip().strip('"').strip("'")
                p = Path(val)
                if p.exists():
                    return p
    for candidate in (ROOT.parent / "Website", ROOT.parents[1] / "Website"):
        if (candidate / "astro.config.mjs").exists():
            return candidate
    raise FileNotFoundError(
        "Cannot locate the Astro site root. "
        "Set website_root in config.toml (copy config.toml.example)."
    )


SITE_ROOT = _resolve_site_root()
DASHBOARDS_OUT = SITE_ROOT / "public" / "research" / "spacex-social-wealth-fund"

IPO_FACTS_YAML = FACTS / "ipo_facts.yaml"
PREDICTIONS_YAML = PREDICTIONS / "predictions.yaml"
INJECTED_FACTS_JSON = PROCESSED / "injected_facts.json"


def raw_dir(source: str, date: str | None = None) -> Path:
    """data/raw/<source>/<YYYY-MM-DD>/ — immutable dated snapshots."""
    date = date or _dt.date.today().isoformat()
    return RAW / source / date


def ensure_dirs() -> None:
    for d in (DATA, FACTS, PREDICTIONS, RAW, PROCESSED, MODELS, DASHBOARDS_OUT):
        d.mkdir(parents=True, exist_ok=True)
