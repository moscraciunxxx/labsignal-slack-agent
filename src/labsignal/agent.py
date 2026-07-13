"""LabSignal's entry point: Claude reasoning over MCP tools, with a rule-based fallback.

When an Anthropic key is configured, every request is answered by Claude choosing
tools from the MCP server. Without one, LabSignal degrades to the deterministic
keyword router below -- less capable, but it still answers and costs nothing.
"""

from __future__ import annotations

import logging

from .knowledge import search_protocols
from .tools import (
    build_research_brief,
    detect_risks,
    extract_action_items,
    format_actions,
    format_demo_card,
    format_plan,
    format_protocols,
    format_research_brief,
    format_risks,
    plan_experiment,
    summarize_update,
)

log = logging.getLogger(__name__)


class LabSignalAgent:
    def __init__(self, brain=None) -> None:
        self._brain = brain

    @property
    def is_reasoning(self) -> bool:
        return self._brain is not None

    def respond(self, text: str, channel_id: str | None = None) -> tuple[str, list[str]]:
        """Answer a request. Returns the reply text and the MCP tools used (if any)."""
        cleaned = _strip_bot_mention(text)

        if self._brain is not None and cleaned:
            try:
                return self._brain.respond(cleaned, channel_id)
            except Exception:
                # Degrade, but say so. A silent fallback is indistinguishable from a
                # real answer, which is how a demo dies without anyone noticing.
                log.exception("model/MCP path failed; falling back to the rule-based router")
                return (
                    ":warning: _I couldn't reach my model just now, so this is a "
                    "keyword-matched answer rather than a reasoned one._\n\n"
                    + self._route(cleaned),
                    [],
                )

        return (self._route(cleaned), [])

    # -- deterministic fallback -------------------------------------------

    def _route(self, cleaned: str) -> str:
        lower = cleaned.lower()

        if lower in {"demo", "help", "menu", ""}:
            return format_demo_card()

        if lower.startswith("actions") or "action items" in lower:
            body = cleaned.partition(" ")[2] if lower.startswith("actions") else cleaned
            return format_actions(extract_action_items(body))

        if lower.startswith("brief") or lower.startswith("handoff"):
            return format_research_brief(build_research_brief(cleaned.partition(" ")[2]))

        if lower.startswith("risks") or lower.startswith("risk"):
            return format_risks(detect_risks(cleaned.partition(" ")[2]))

        if lower.startswith("plan") or lower.startswith("checklist"):
            return format_plan(plan_experiment(cleaned.partition(" ")[2]))

        if lower.startswith("protocol") or "protocol" in lower or "sop" in lower:
            query = cleaned.partition(" ")[2] if lower.startswith("protocol") else cleaned
            return format_protocols(search_protocols(query))

        if lower.startswith("summarize") or lower.startswith("summary"):
            return f"Summary: {summarize_update(cleaned.partition(' ')[2])}"

        return (
            "I can help with `brief`, `actions`, `risks`, `plan`, `protocol`, or `summarize`.\n"
            "Example: `brief Alice will QC CA1 recordings by Friday. Two channels are saturated.`"
        )


def _strip_bot_mention(text: str) -> str:
    return " ".join(part for part in text.split() if not part.startswith("<@")).strip()
