"""Small demo knowledge base for neuroscience research ops."""

from __future__ import annotations

import re

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

STOPWORDS = {
    "and",
    "are",
    "before",
    "for",
    "from",
    "need",
    "needs",
    "should",
    "that",
    "the",
    "this",
    "today",
    "will",
    "with",
}

EXPERIMENT_PLANS = [
    {
        "id": "ca1-neuropixels",
        "title": "CA1 Neuropixels session checklist",
        "tags": {"ca1", "neuropixels", "hippocampus", "recording", "qc"},
        "steps": [
            "Confirm animal ID, cohort, probe map, and task condition before recording.",
            "Run impedance/probe health check and note any suspect channels.",
            "Record a short baseline segment and verify theta-band signal quality.",
            "After acquisition, flag saturated, flatline, and high-variance channels.",
            "Export rejected channel IDs and link them to the session metadata.",
        ],
    },
    {
        "id": "two-photon-calcium",
        "title": "Two-photon calcium imaging checklist",
        "tags": {"two-photon", "calcium", "imaging", "motion", "suite2p"},
        "steps": [
            "Verify field of view, laser power, frame rate, and imaging depth.",
            "Capture a stable baseline period before the behavioral task starts.",
            "Run rigid motion correction and inspect framewise displacement.",
            "Use non-rigid correction only when local drift remains visible.",
            "Export ROI QC notes with inclusion and exclusion criteria.",
        ],
    },
    {
        "id": "open-science-release",
        "title": "Open science release checklist",
        "tags": {"release", "data", "paper", "reproducibility", "sharing"},
        "steps": [
            "Confirm consent, privacy, and institutional sharing constraints.",
            "De-identify metadata and remove internal-only paths or credentials.",
            "Publish analysis scripts with pinned dependencies and a quickstart.",
            "Add a data dictionary and explain exclusion criteria.",
            "Run a clean-room reproduction check from the README.",
        ],
    },
]


def search_protocols(query: str, limit: int = 3) -> list[dict[str, str]]:
    words = _keywords(query)
    min_score = 2 if len(words) >= 2 else 1
    scored = []
    for item in PROTOCOLS:
        haystack = _keywords(f"{item['title']} {' '.join(item['tags'])} {item['body']}")
        score = len(words & haystack)
        if score >= min_score:
            scored.append((score, item))
    scored.sort(key=lambda row: row[0], reverse=True)
    return [
        {"id": item["id"], "title": item["title"], "body": item["body"]}
        for _, item in scored[:limit]
    ]


def find_experiment_plan(query: str) -> dict[str, object] | None:
    words = _keywords(query)
    scored = []
    for item in EXPERIMENT_PLANS:
        haystack = set(item["title"].lower().split()) | item["tags"]
        score = len(words & haystack)
        if score:
            scored.append((score, item))
    if not scored:
        return None
    scored.sort(key=lambda row: row[0], reverse=True)
    return scored[0][1]


def _keywords(text: str) -> set[str]:
    return {w for w in re.findall(r"[a-z0-9-]+", text.lower()) if len(w) > 2 and w not in STOPWORDS}
