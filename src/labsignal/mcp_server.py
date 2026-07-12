"""MCP-compatible tool server for LabSignal.

This is the only path through which the agent reaches its capabilities. The Slack
app spawns this module over stdio, discovers the tools below, and lets Claude
choose which to call. Nothing in the Slack layer imports `tools.py` directly.

Tool docstrings are prescriptive about *when* to call, not just what the tool
does -- that is what the model reads to decide.
"""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from .config import Config
from .knowledge import search_protocols as _search_protocols
from .slack_read import fetch_channel_messages as _fetch_channel_messages
from .tools import build_research_brief as _build_research_brief
from .tools import detect_risks as _detect_risks
from .tools import extract_action_items as _extract_action_items
from .tools import plan_experiment as _plan_experiment
from .tools import summarize_update as _summarize_update

mcp = FastMCP("labsignal")


@mcp.tool()
def read_slack_channel(channel_id: str, limit: int = 40) -> list[dict[str, str]]:
    """Read recent messages from a Slack channel.

    Call this first whenever the user refers to a discussion, a channel, or "what
    we decided" instead of pasting the text themselves. `channel_id` is a Slack
    channel ID such as C0123456789. Returns messages oldest-first, each with the
    author's display name and an ISO-8601 timestamp.
    """
    return _fetch_channel_messages(Config().slack_bot_token, channel_id, limit)


@mcp.tool()
def search_protocols(query: str) -> list[dict[str, str]]:
    """Search the lab's neuroscience protocol knowledge base.

    Call this when the user asks how a procedure is done, mentions an SOP, or when
    a handoff would be more useful with the lab's own protocol text attached.
    """
    return _search_protocols(query)


@mcp.tool()
def extract_action_items(text: str) -> list[dict[str, str]]:
    """Extract owner/task/deadline action items from a research update.

    Call this when the user wants to know who owes what, or to turn a loose
    discussion into assignable next steps.
    """
    return _extract_action_items(text)


@mcp.tool()
def summarize_update(text: str) -> str:
    """Compress a long research update down to its leading claim."""
    return _summarize_update(text)


@mcp.tool()
def detect_risks(text: str) -> list[dict[str, str]]:
    """Flag QC, schedule, governance, and reproducibility risks in a research update.

    Call this before any handoff or data release, and whenever the user asks what
    could go wrong or what is blocking a recording session.
    """
    return _detect_risks(text)


@mcp.tool()
def build_research_brief(text: str) -> dict[str, object]:
    """Build a structured lab handoff: summary, actions, risks, and relevant protocols.

    Call this for handoff, standup, and "catch me up" requests. Pass the raw
    discussion text -- read it with `read_slack_channel` first if the user did not
    paste it in.
    """
    return _build_research_brief(text)


@mcp.tool()
def plan_experiment(query: str) -> dict[str, object]:
    """Return the lab's checklist for a matching neuroscience workflow.

    Call this when the user is about to run a session and wants to know the steps.
    """
    return _plan_experiment(query)


if __name__ == "__main__":
    mcp.run()
