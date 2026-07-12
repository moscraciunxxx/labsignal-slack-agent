"""Claude tool-use loop. Every tool it can call is discovered from the MCP server."""

from __future__ import annotations

import logging

from anthropic import AsyncAnthropic
from anthropic.lib.tools.mcp import async_mcp_tool

from .mcp_client import MCPToolSession

log = logging.getLogger(__name__)

SYSTEM = """You are LabSignal, a research-operations agent for a neuroscience lab, \
answering inside Slack.

Your job is to turn scattered lab chatter into decisions people can act on: handoffs \
between shifts, who owes what by when, what could invalidate a recording, and which \
protocol applies.

Working rules:
- You have no knowledge of the lab except what your tools return. Never invent an owner, \
  a deadline, a session ID, or a protocol step. If a tool returns nothing, say so.
- When the user refers to a discussion, a channel, or "what we decided" without pasting \
  the text, call read_slack_channel first to get the real messages, then reason over them.
- Prefer build_research_brief for handoff and catch-up requests; it composes the other \
  tools for you.
- Attribute the specifics. "Two channels saturated (Alice, Tue)" beats "there are QC risks."

Answer in Slack mrkdwn: *bold* (never **bold**), `code`, and "- " bullets. No markdown \
headings. Lead with the answer, then the supporting detail. Keep it under ~200 words \
unless the user asked for a full brief."""


class ClaudeBrain:
    """Wraps the Anthropic tool-use loop. Tools come from MCP, not from Python imports."""

    def __init__(self, mcp: MCPToolSession, api_key: str, model: str) -> None:
        self._mcp = mcp
        self._model = model
        self._client = AsyncAnthropic(api_key=api_key)

    def respond(self, question: str, channel_id: str | None = None) -> tuple[str, list[str]]:
        """Answer a question. Returns the reply and the MCP tools Claude actually called."""
        return self._mcp.run(self._answer(question, channel_id))

    async def _answer(self, question: str, channel_id: str | None) -> tuple[str, list[str]]:
        if channel_id:
            question = (
                f"{question}\n\n(The user is in Slack channel {channel_id}. Use that channel_id "
                f"if you need to read the conversation.)"
            )

        tools = [async_mcp_tool(tool, self._mcp.session) for tool in self._mcp.tools]
        runner = self._client.beta.messages.tool_runner(
            model=self._model,
            max_tokens=4096,
            system=SYSTEM,
            thinking={"type": "adaptive"},
            output_config={"effort": "medium"},
            tools=tools,
            messages=[{"role": "user", "content": question}],
        )

        called: list[str] = []
        final = None
        async for message in runner:
            final = message
            for block in message.content:
                if block.type == "tool_use" and block.name not in called:
                    called.append(block.name)

        if final is None:
            raise RuntimeError("Claude returned no message.")
        if final.stop_reason == "refusal":
            return ("I can't help with that request.", called)

        text = "\n".join(b.text for b in final.content if b.type == "text" and b.text).strip()
        log.info("answered via MCP tools: %s", called or "none")
        return (text or "I could not find anything to report.", called)
