"""MCP-compatible tool server for LabSignal."""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from .knowledge import search_protocols as _search_protocols
from .tools import build_research_brief as _build_research_brief
from .tools import detect_risks as _detect_risks
from .tools import extract_action_items as _extract_action_items
from .tools import plan_experiment as _plan_experiment
from .tools import summarize_update as _summarize_update

mcp = FastMCP("labsignal")


@mcp.tool()
def search_protocols(query: str) -> list[dict[str, str]]:
    """Search the neuroscience protocol knowledge base."""
    return _search_protocols(query)


@mcp.tool()
def extract_action_items(text: str) -> list[dict[str, str]]:
    """Extract owner/task/deadline action items from a research update."""
    return _extract_action_items(text)


@mcp.tool()
def summarize_update(text: str) -> str:
    """Create a concise summary of a research update."""
    return _summarize_update(text)


@mcp.tool()
def detect_risks(text: str) -> list[dict[str, str]]:
    """Detect QC, schedule, governance, and reproducibility risks."""
    return _detect_risks(text)


@mcp.tool()
def build_research_brief(text: str) -> dict[str, object]:
    """Build a structured lab handoff with summary, actions, risks, and protocols."""
    return _build_research_brief(text)


@mcp.tool()
def plan_experiment(query: str) -> dict[str, object]:
    """Return a checklist for a matching neuroscience workflow."""
    return _plan_experiment(query)


if __name__ == "__main__":
    mcp.run()
