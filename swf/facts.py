"""Load the single source of truth (ipo_facts.yaml) and expose flat, typed accessors.

Usage:
    from swf import facts
    f = facts.load()
    f.get("offering.ipo_price_usd")          -> 135.0
    f.fmt_usd("offering.gross_proceeds_usd")  -> "$75.0B"
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any
import re
import yaml

from . import paths

# PyYAML (YAML 1.1) only treats an exponent as a float when it carries a sign (e+9),
# so "75.0e9" loads as a string. Coerce any leaf that is a clean numeric literal.
_NUM_RE = re.compile(r"^[-+]?(\d+\.?\d*|\.\d+)([eE][-+]?\d+)?$")


def _coerce(v: Any) -> Any:
    if isinstance(v, str) and _NUM_RE.match(v.strip()):
        f = float(v)
        return int(f) if f.is_integer() and "e" not in v.lower() and "." not in v else f
    return v


def _walk(node: Any, prefix: str, out: dict[str, Any]) -> None:
    """Flatten the nested yaml into dotted keys, unwrapping {value:..} leaves."""
    if isinstance(node, dict):
        if "value" in node and not any(isinstance(v, dict) for k, v in node.items() if k != "value"):
            out[prefix.rstrip(".")] = _coerce(node["value"])
            # keep the metadata too, namespaced
            for k, v in node.items():
                if k != "value":
                    out[f"{prefix}{k}"] = v
            return
        for k, v in node.items():
            _walk(v, f"{prefix}{k}." if prefix else f"{k}.", out)
    else:
        out[prefix.rstrip(".")] = _coerce(node)


@dataclass
class Facts:
    raw: dict[str, Any]
    flat: dict[str, Any]

    def get(self, dotted: str, default: Any = None) -> Any:
        return self.flat.get(dotted, default)

    # --- formatting helpers used by both prose-injection and dashboards ---
    @staticmethod
    def human_usd(x: float, decimals: int = 2) -> str:
        ax = abs(x)
        for thresh, suffix in ((1e12, "T"), (1e9, "B"), (1e6, "M"), (1e3, "K")):
            if ax >= thresh:
                s = f"{x / thresh:.{decimals}f}".rstrip("0").rstrip(".")
                return f"${s}{suffix}"
        return f"${x:,.0f}"

    def fmt_usd(self, dotted: str) -> str:
        return self.human_usd(float(self.get(dotted)))

    def pct(self, dotted: str) -> str:
        return f"{float(self.get(dotted)) * 100:.1f}%"


def load() -> Facts:
    with open(paths.IPO_FACTS_YAML, "r", encoding="utf-8") as fh:
        raw = yaml.safe_load(fh)
    flat: dict[str, Any] = {}
    _walk(raw, "", flat)
    return Facts(raw=raw, flat=flat)


if __name__ == "__main__":  # quick smoke test
    f = load()
    for k in ("offering.ipo_price_usd", "offering.gross_proceeds_usd",
              "first_day.close_usd", "financials_fy2025.revenue_total_usd",
              "financials_fy2025.implied_ps_trailing"):
        print(f"{k:45s} = {f.get(k)!r:>16}  ({f.human_usd(f.get(k)) if isinstance(f.get(k),(int,float)) else ''})")
