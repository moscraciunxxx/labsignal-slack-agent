"""The MCP server is the agent's only path to its tools, so exercise it for real."""

import pytest

from labsignal.agent import LabSignalAgent
from labsignal.blocks import answer_blocks
from labsignal.mcp_client import MCPToolSession
from labsignal.slack_read import fetch_channel_messages

EXPECTED_TOOLS = {
    "read_slack_channel",
    "search_protocols",
    "extract_action_items",
    "summarize_update",
    "detect_risks",
    "build_research_brief",
    "plan_experiment",
}


@pytest.fixture(scope="module")
def mcp():
    session = MCPToolSession()
    session.start()
    yield session
    session.stop()


def test_server_advertises_every_tool(mcp):
    assert set(mcp.tool_names()) == EXPECTED_TOOLS


def test_tools_carry_when_to_call_guidance(mcp):
    """Claude picks tools from these descriptions, so they must say when to call."""
    read = next(t for t in mcp.tools if t.name == "read_slack_channel")
    assert "Call this first" in read.description


def test_tool_call_round_trips_over_stdio(mcp):
    result = mcp.run(
        mcp.session.call_tool(
            "extract_action_items",
            {"text": "Alice will QC CA1 recordings by Friday."},
        )
    )
    assert not result.isError
    items = result.structuredContent["result"]
    assert items[0]["owner"] == "Alice"
    assert items[0]["deadline"].lower() == "friday"


def test_read_slack_channel_reports_a_missing_token():
    """Without a token the tool must fail loudly, never fabricate messages."""
    with pytest.raises(RuntimeError, match="SLACK_BOT_TOKEN"):
        fetch_channel_messages("", "C0000000000")


def test_answer_blocks_footer_credits_the_mcp_tools():
    blocks = answer_blocks("*Handoff*\n- Alice owes QC", ["read_slack_channel", "detect_risks"])
    assert blocks[0]["text"]["text"].startswith("*Handoff*")
    footer = blocks[-1]["elements"][0]["text"]
    assert "read_slack_channel" in footer and "detect_risks" in footer


def test_answer_blocks_splits_text_over_slacks_section_limit():
    blocks = answer_blocks("\n".join(["line"] * 2000), [])
    assert len(blocks) > 1
    assert all(len(b["text"]["text"]) <= 3000 for b in blocks)


def test_agent_reports_the_tools_the_brain_used():
    class FakeBrain:
        def respond(self, question, channel_id=None):
            return ("Alice owes CA1 QC by Friday.", ["read_slack_channel", "extract_action_items"])

    text, tools_used = LabSignalAgent(FakeBrain()).respond("who owes what?", "C123")
    assert text == "Alice owes CA1 QC by Friday."
    assert tools_used == ["read_slack_channel", "extract_action_items"]


def test_agent_falls_back_when_the_brain_fails():
    class BrokenBrain:
        def respond(self, question, channel_id=None):
            raise RuntimeError("Anthropic API is down")

    text, tools_used = LabSignalAgent(BrokenBrain()).respond("plan ca1 neuropixels qc")
    assert "CA1 Neuropixels" in text
    assert tools_used == []
