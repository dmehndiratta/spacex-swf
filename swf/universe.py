"""The ticker universe used across fetch, event studies, and the live tracker."""

SUBJECT = "SPCX"

# Benchmarks
BENCHMARKS = {
    "^NDX": "Nasdaq-100",
    "^GSPC": "S&P 500",
    "^IXIC": "Nasdaq Composite",
}

# Listed space / satellite peers (§4.6 peer event study)
SPACE_PEERS = {
    "RKLB": "Rocket Lab",
    "ASTS": "AST SpaceMobile",
    "PL": "Planet Labs",
    "IRDM": "Iridium",
    "SESG.PA": "SES",
    "GSAT": "Globalstar",
    "VSAT": "Viasat",
}

# Defense primes (read-through / launch-adjacent)
DEFENSE_PEERS = {
    "LMT": "Lockheed Martin",
    "NOC": "Northrop Grumman",
    "RTX": "RTX",
    "BA": "Boeing",
}

# The Musk complex read-through
MUSK_COMPLEX = {"TSLA": "Tesla"}

# AI / compute proxy for the xAI segment narrative
AI_PROXY = {"NVDA": "Nvidia", "MSFT": "Microsoft", "GOOGL": "Alphabet"}

# Everything we pull a live price history for.
PEER_NAMES = {**SPACE_PEERS, **DEFENSE_PEERS, **MUSK_COMPLEX, **AI_PROXY}
ALL_LIVE = [SUBJECT] + list(BENCHMARKS) + list(PEER_NAMES)

# Peers whose abnormal returns we test around the SPCX debut (the spillover study).
EVENT_STUDY_PEERS = list(SPACE_PEERS) + list(DEFENSE_PEERS) + list(MUSK_COMPLEX)
