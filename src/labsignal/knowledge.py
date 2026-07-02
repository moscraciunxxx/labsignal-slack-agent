"""Small demo knowledge base for neuroscience research ops."""

from __future__ import annotations

PROTOCOLS = [
    {
        "id": "ca1-neuropixels-qc",
        "title": "CA1 Neuropixels QC",
        "tags": {"ca1", "neuropixels", "qc", "hippocampus"},
        "body": (
            "Check probe map, remove channels with flatline or saturated variance, "
            "verify theta-band power, and save rejected channel IDs before spike sorting."
        ),
    },
    {
        "id": "two-photon-motion",
        "title": "Two-photon motion correction",
        "tags": {"calcium", "two-photon", "motion", "imaging"},
        "body": (
            "Run rigid correction first, inspect framewise displacement, then use non-rigid "
            "correction only when local drift remains visible in cell-body regions."
        ),
    },
    {
        "id": "open-science-release",
        "title": "Open science release checklist",
        "tags": {"release", "data", "reproducibility", "paper"},
        "body": (
            "Before sharing data, verify consent constraints, de-identify metadata, publish "
            "analysis scripts, and include a short data dictionary."
        ),
    },
]


def search_protocols(query: str, limit: int = 3) -> list[dict[str, str]]:
    words = {w.strip(".,:;!?()[]").lower() for w in query.split() if len(w) > 2}
    scored = []
    for item in PROTOCOLS:
        haystack = set(item["title"].lower().split()) | item["tags"] | set(item["body"].lower().split())
        score = len(words & haystack)
        if score:
            scored.append((score, item))
    scored.sort(key=lambda row: row[0], reverse=True)
    return [
        {"id": item["id"], "title": item["title"], "body": item["body"]}
        for _, item in scored[:limit]
    ]

