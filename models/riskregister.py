"""Structured risk register for Part I (plan.md §4.4), scored on likelihood x impact
(1-5 each) and grouped by category, rendered as an interactive heatmap. Scores are
analyst judgements, stated as such; each item carries a one-line rationale and a quantified
hook into the prospectus/Part II data where one exists.
"""
from __future__ import annotations

# severity = likelihood * impact (1..25)
REGISTER = [
    # category, risk, likelihood(1-5), impact(1-5), note
    ("Control / governance", "Super-voting founder control", 5, 4,
     "Dual-class structure: public float holds large economic but minimal voting share."),
    ("Control / governance", "Key-person (Musk) risk", 4, 5,
     "Strategy, capital access, and narrative are tightly bound to one individual."),
    ("Control / governance", "Related-party dynamics post-xAI merger", 4, 3,
     "Intra-complex transactions (SpaceX/xAI/X/Tesla) blur arms-length pricing."),
    ("Customer concentration", "U.S. government revenue dependence", 4, 4,
     "NASA/DoD/Space Force are anchor customers; quantified against Part II USAspending data."),
    ("Regulatory", "FAA launch licensing throughput", 3, 3,
     "Starship cadence gated by environmental + launch-license review."),
    ("Regulatory", "FCC spectrum & orbital-debris rules", 3, 4,
     "Starlink economics depend on spectrum grants and debris-mitigation regime."),
    ("Regulatory", "Antitrust / CFIUS / ITAR export controls", 3, 4,
     "Scale + national-security entanglement invites scrutiny on both sides."),
    ("Competition", "Amazon Kuiper / Blue Origin", 4, 3,
     "Well-capitalised direct competitor in broadband + launch."),
    ("Competition", "Chinese state constellations & launch", 3, 3,
     "Guowang/Qianfan and state launch erode the international TAM."),
    ("Competition", "Frontier-AI competition for xAI", 5, 3,
     "OpenAI/Anthropic/Google ahead on several axes; xAI burns to stay in the race."),
    ("Financial", "Consolidated -$4.9B net loss / xAI burn", 4, 4,
     "AI segment -$6.35B op loss, $12.7B capex; consolidated GAAP loss."),
    ("Financial", "Capex intensity & dilution path", 4, 3,
     "Heavy launch + compute capex implies further raises / greenshoe dilution."),
    ("Financial", "Rate sensitivity (long-duration cash flows)", 3, 4,
     "Valuation is almost entirely terminal value; highly rate-sensitive."),
    ("Market structure", "Lockup overhang", 4, 3,
     "Staged unlocks (90/180/270/365d) are recurring supply shocks — see lockup model."),
    ("Market structure", "Float scarcity / single-name concentration", 3, 3,
     "Small free float vs mega-cap inclusion creates volatility + index distortion."),
    ("Valuation / sentiment", "Multiple compression if narrative turns", 4, 5,
     "Reverse-DCF implies ~56% revenue CAGR to justify $1.77T; little margin for error."),
]


def risk_register() -> dict:
    items = []
    for cat, risk, like, imp, note in REGISTER:
        items.append({
            "category": cat, "risk": risk, "likelihood": like, "impact": imp,
            "severity": like * imp, "note": note,
        })
    items.sort(key=lambda d: d["severity"], reverse=True)
    cats = sorted({i["category"] for i in items})
    return {
        "items": items, "categories": cats,
        "n": len(items),
        "top3": [i["risk"] for i in items[:3]],
        "mean_severity": round(sum(i["severity"] for i in items) / len(items), 1),
    }


if __name__ == "__main__":
    rr = risk_register()
    print("risks:", rr["n"], "mean severity:", rr["mean_severity"], "top3:", rr["top3"])
