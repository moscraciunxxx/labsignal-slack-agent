"""Core LabSignal agent logic, independent from Slack transport."""

from __future__ import annotations

from .knowledge import search_protocols
from .tools import extract_action_items, format_actions, format_protocols, summarize_update


class LabSignalAgent:
    def respond(self, text: str) -> str:
        cleaned = _strip_bot_mention(text)
        lower = cleaned.lower()

        if lower.startswith("actions") or "action items" in lower:
            body = cleaned.partition(" ")[2] if lower.startswith("actions") else cleaned
            return format_actions(extract_action_items(body))

        if lower.startswith("protocol") or "protocol" in lower or "sop" in lower:
            query = cleaned.partition(" ")[2] if lower.startswith("protocol") else cleaned
            return format_protocols(search_protocols(query))

        if lower.startswith("summarize") or lower.startswith("summary"):
            body = cleaned.partition(" ")[2]
            return f"Summary: {summarize_update(body)}"

        return (
            "I can help with `actions`, `protocol`, or `summarize`.\n"
            "Example: `actions Alice will QC CA1 recordings by Friday.`"
        )


def _strip_bot_mention(text: str) -> str:
    return " ".join(part for part in text.split() if not part.startswith("<@")).strip()

