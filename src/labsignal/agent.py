"""Core LabSignal agent logic, independent from Slack transport."""

from __future__ import annotations

from .knowledge import search_protocols
from .tools import (
    build_research_brief,
    detect_risks,
    extract_action_items,
    format_actions,
    format_plan,
    format_protocols,
    format_demo_card,
    format_research_brief,
    format_risks,
    plan_experiment,
    summarize_update,
)


class LabSignalAgent:
    def respond(self, text: str) -> str:
        cleaned = _strip_bot_mention(text)
        lower = cleaned.lower()

        if lower in {"demo", "help", "menu", ""}:
            return format_demo_card()

        if lower.startswith("actions") or "action items" in lower:
            body = cleaned.partition(" ")[2] if lower.startswith("actions") else cleaned
            return format_actions(extract_action_items(body))

        if lower.startswith("brief") or lower.startswith("handoff"):
            body = cleaned.partition(" ")[2]
            return format_research_brief(build_research_brief(body))

        if lower.startswith("risks") or lower.startswith("risk"):
            body = cleaned.partition(" ")[2]
            return format_risks(detect_risks(body))

        if lower.startswith("plan") or lower.startswith("checklist"):
            query = cleaned.partition(" ")[2]
            return format_plan(plan_experiment(query))

        if lower.startswith("protocol") or "protocol" in lower or "sop" in lower:
            query = cleaned.partition(" ")[2] if lower.startswith("protocol") else cleaned
            return format_protocols(search_protocols(query))

        if lower.startswith("summarize") or lower.startswith("summary"):
            body = cleaned.partition(" ")[2]
            return f"Summary: {summarize_update(body)}"

        return (
            "I can help with `brief`, `actions`, `risks`, `plan`, `protocol`, or `summarize`.\n"
            "Example: `brief Alice will QC CA1 recordings by Friday. Two channels are saturated.`"
        )


def _strip_bot_mention(text: str) -> str:
    return " ".join(part for part in text.split() if not part.startswith("<@")).strip()
