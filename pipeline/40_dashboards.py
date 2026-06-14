"""Stage 40 — regenerate every dashboard HTML from data/processed into the site's
public dir (../../public/research/spacex-social-wealth-fund/). Self-contained static files."""
from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from swf import paths

import importlib


def log(m): print(f"[40_dashboards] {m}", flush=True)


def main():
    paths.DASHBOARDS_OUT.mkdir(parents=True, exist_ok=True)
    builders = []
    for mod_name in ("dashboards.part1", "dashboards.part1_interactive",
                     "dashboards.part2", "dashboards.part3", "dashboards.part4"):
        try:
            mod = importlib.import_module(mod_name)
        except ModuleNotFoundError:
            continue
        builders += getattr(mod, "STATIC_BUILDERS", [])
        builders += getattr(mod, "INTERACTIVE_BUILDERS", [])
        builders += getattr(mod, "BUILDERS", [])

    written = 0
    for build in builders:
        try:
            fname, html = build()
            (paths.DASHBOARDS_OUT / fname).write_text(html, encoding="utf-8")
            log(f"  ok {fname} ({len(html)//1024} KB)")
            written += 1
        except Exception as e:
            import traceback
            log(f"  ! {build.__name__}: {type(e).__name__}: {e}")
            traceback.print_exc()
    log(f"wrote {written} dashboards -> {paths.DASHBOARDS_OUT}")


if __name__ == "__main__":
    main()
