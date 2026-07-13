"""Grok tool-use loop over the same MCP tools.

Identical contract to ClaudeBrain: the model is handed tool schemas discovered from
the MCP server and decides what to call. Only the wire format differs -- xAI speaks
the OpenAI function-calling schema, so MCP's JSON Schema is passed straight through.
"""

from __future__ import annotations

import json
import logging

from openai import AsyncOpenAI

from .brain import SYSTEM
from .mcp_client import MCPToolSession

log = logging.getLogger(__name__)

XAI_BASE_URL = "https://api.x.ai/v1"
MAX_STEPS = 8  # tool-calling rounds before we stop, so a loop can't run away


class GrokBrain:
    def __init__(self, mcp: MCPToolSession, api_key: str, model: str) -> None:
        self._mcp = mcp
        self._model = model
        # Retry hard: a dropped connection would otherwise surface as the keyword
        # fallback, which reads like a correct answer rather than a failure.
        self._client = AsyncOpenAI(
            api_key=api_key,
            base_url=XAI_BASE_URL,
            max_retries=5,
            timeout=90.0,
        )

    def respond(self, question: str, channel_id: str | None = None) -> tuple[str, list[str]]:
        return self._mcp.run(self._answer(question, channel_id))

    async def _answer(self, question: str, channel_id: str | None) -> tuple[str, list[str]]:
        if channel_id:
            question = (
                f"{question}\n\n(The user is in Slack channel {channel_id}. Use that channel_id "
                f"if you need to read the conversation.)"
            )

        tools = [
            {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description or "",
                    "parameters": tool.inputSchema,
                },
            }
            for tool in self._mcp.tools
        ]
        messages: list[dict] = [
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": question},
        ]

        called: list[str] = []
        for step in range(MAX_STEPS):
            # The agent knows nothing about the lab except what its tools return, so it
            # must consult at least one before answering. Left on "auto", Grok will
            # sometimes reply from an empty context -- which reads as confident invention.
            # After the first call it can decide for itself when it is done.
            tool_choice = "required" if step == 0 else "auto"
            response = await self._client.chat.completions.create(
                model=self._model,
                messages=messages,
                tools=tools,
                tool_choice=tool_choice,
            )
            message = response.choices[0].message
            if not message.tool_calls:
                text = (message.content or "").strip()
                log.info("answered via MCP tools: %s", called or "none")
                return (text or "I could not find anything to report.", called)

            messages.append(message.model_dump(exclude_none=True))
            for call in message.tool_calls:
                name = call.function.name
                if name not in called:
                    called.append(name)
                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": call.id,
                        "content": await self._call_mcp(name, call.function.arguments),
                    }
                )

        return ("I hit my tool-call limit before finishing that one.", called)

    async def _call_mcp(self, name: str, raw_arguments: str) -> str:
        """Run one MCP tool and flatten its result into text the model can read."""
        try:
            arguments = json.loads(raw_arguments or "{}")
            result = await self._mcp.session.call_tool(name, arguments)
        except Exception as error:  # hand the failure back so the model can adapt
            log.warning("MCP tool %s failed: %s", name, error)
            return f"Error calling {name}: {error}"

        if result.structuredContent is not None:
            return json.dumps(result.structuredContent.get("result", result.structuredContent))
        text = "\n".join(b.text for b in result.content if getattr(b, "type", "") == "text")
        if result.isError:
            return f"Error calling {name}: {text}"
        return text or "(no result)"
