"""Deterministic tools exposed to Slack and MCP."""

from __future__ import annotations

import re

from .knowledge import search_protocols


def extract_action_items(text: str) -> list[dict[str, str]]:
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    items: list[dict[str, str]] = []
    cue = re.compile(r"\b(will|should|needs to|need to|by|before|todo|action)\b", re.I)
    owner_re = re.compile(r"\b([A-Z][a-z]+)\b")
    date_re = re.compile(r"\b(today|tomorrow|friday|monday|tuesday|wednesday|thursday|next week|\d{1,2}/\d{1,2})\b", re.I)
    for sentence in sentences:
        if not sentence or not cue.search(sentence):
            continue
        owner = owner_re.search(sentence)
        deadline = date_re.search(sentence)
        items.append(
            {
                "owner": owner.group(1) if owner else "unassigned",
                "task": sentence.strip(),
                "deadline": deadline.group(1) if deadline else "not specified",
            }
        )
    return items


def summarize_update(text: str) -> str:
    compact = " ".join(text.split())
    if len(compact) <= 260:
        return compact
    first = re.split(r"(?<=[.!?])\s+", compact)[0]
    return first[:260].strip()


def format_actions(items: list[dict[str, str]]) -> str:
    if not items:
        return "No clear action items found. Try including an owner, task, and deadline."
    lines = ["Action items:"]
    for item in items:
        lines.append(f"- {item['owner']}: {item['task']} Deadline: {item['deadline']}.")
    return "\n".join(lines)


def format_protocols(results: list[dict[str, str]]) -> str:
    if not results:
        return "I could not find a matching protocol in the local knowledge base."
    lines = ["Protocol matches:"]
    for result in results:
        lines.append(f"- {result['title']} ({result['id']}): {result['body']}")
    return "\n".join(lines)

