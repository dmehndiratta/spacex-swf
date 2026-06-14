"""Chain the pipeline stages. Each stage is independently runnable; this just sequences them.

  python run.py                 full pipeline (fetch -> clean -> models -> score -> dashboards -> facts)
  python run.py --offline       skip network fetch; rebuild from last-good snapshots
  python run.py --stage 40      run a single stage by number
  python run.py --from 20       run from a stage onward
"""
from __future__ import annotations
import sys, subprocess, argparse, time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PY = sys.executable
STAGES = [
    ("00", "pipeline/00_fetch.py"),
    ("10", "pipeline/10_clean.py"),
    ("20", "pipeline/20_models.py"),
    ("30", "pipeline/30_score.py"),
    ("40", "pipeline/40_dashboards.py"),
    ("50", "pipeline/50_facts.py"),
]


def run(script: str, extra: list[str]) -> int:
    return subprocess.call([PY, str(ROOT / script), *extra], cwd=ROOT)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--offline", action="store_true")
    ap.add_argument("--stage", help="run only this stage number, e.g. 40")
    ap.add_argument("--from", dest="from_stage", help="run from this stage onward")
    args = ap.parse_args()

    selected = STAGES
    if args.stage:
        selected = [s for s in STAGES if s[0] == args.stage]
    elif args.from_stage:
        idx = [i for i, s in enumerate(STAGES) if s[0] == args.from_stage]
        selected = STAGES[idx[0]:] if idx else STAGES

    t0 = time.time()
    for num, script in selected:
        extra = ["--offline"] if (num == "00" and args.offline) else []
        print(f"\n=== stage {num}: {script} {' '.join(extra)} ===", flush=True)
        rc = run(script, extra)
        if rc != 0:
            print(f"!!! stage {num} failed (rc={rc}) — stopping", flush=True)
            sys.exit(rc)
    print(f"\n=== pipeline complete in {time.time()-t0:.1f}s ===")


if __name__ == "__main__":
    main()
