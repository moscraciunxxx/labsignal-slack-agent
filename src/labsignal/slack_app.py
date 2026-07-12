"""Slack Socket Mode app: assistant threads, channel mentions, and a slash command."""

from __future__ import annotations

import logging

from slack_bolt import App, Assistant
from slack_bolt.adapter.socket_mode import SocketModeHandler

from .agent import LabSignalAgent
from .blocks import answer_blocks
from .brain import ClaudeBrain
from .config import Config
from .mcp_client import MCPToolSession

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
log = logging.getLogger("labsignal")

SUGGESTED_PROMPTS = [
    {
        "title": "Hand off this channel",
        "message": "Read this channel and build me a handoff brief for the next shift.",
    },
    {
        "title": "Who owes what?",
        "message": "Read this channel and list every open action item with its owner and deadline.",
    },
    {
        "title": "What could invalidate the session?",
        "message": "Read this channel and flag any QC, schedule, governance, or reproducibility risks.",
    },
    {
        "title": "How do we QC CA1 Neuropixels?",
        "message": "What's our protocol for CA1 Neuropixels QC?",
    },
]

GREETING = (
    "Hi! I'm LabSignal. I read your lab's Slack and turn it into handoffs, action items, "
    "risk flags, and protocol answers.\n\n"
    "Ask me in plain English — or pick one below."
)


def build_agent(config: Config) -> LabSignalAgent:
    """Wire Claude to the MCP server, or fall back to the deterministic router."""
    if not config.reasoning_ready:
        log.warning(
            "ANTHROPIC_API_KEY not set (or LABSIGNAL_FORCE_LOCAL=1). "
            "Running the rule-based fallback; Claude and MCP are disabled."
        )
        return LabSignalAgent()

    mcp = MCPToolSession()
    mcp.start()
    log.info("Claude (%s) reasoning over MCP tools: %s", config.model, mcp.tool_names())
    return LabSignalAgent(ClaudeBrain(mcp, config.anthropic_api_key, config.model))


def build_app(config: Config, agent: LabSignalAgent) -> App:
    app = App(token=config.slack_bot_token)
    assistant = Assistant()

    @assistant.thread_started
    def greet(say, set_suggested_prompts):
        say(GREETING)
        set_suggested_prompts(prompts=SUGGESTED_PROMPTS)

    @assistant.user_message
    def handle_assistant_message(payload, say, set_status, get_thread_context):
        set_status("is reading the lab's Slack...")
        # In an assistant thread the user is "in" whatever channel they opened it from;
        # that context is what lets read_slack_channel find the right conversation.
        context = get_thread_context() or {}
        text, tools_used = agent.respond(payload.get("text", ""), context.get("channel_id"))
        say(text=_fallback(text), blocks=answer_blocks(text, tools_used))

    app.assistant(assistant)

    @app.event("app_mention")
    def handle_mention(event, say):
        text, tools_used = agent.respond(event.get("text", ""), event.get("channel"))
        say(
            text=_fallback(text),
            blocks=answer_blocks(text, tools_used),
            thread_ts=event.get("thread_ts") or event.get("ts"),
        )

    @app.command("/labsignal")
    def handle_command(ack, respond, command):
        ack()
        text, tools_used = agent.respond(command.get("text", ""), command.get("channel_id"))
        respond(
            response_type="in_channel",
            text=_fallback(text),
            blocks=answer_blocks(text, tools_used),
        )

    return app


def _fallback(text: str) -> str:
    """Notification/accessibility text for clients that cannot render blocks."""
    return text[:200] if text else "LabSignal"


def main() -> None:
    config = Config()
    if not config.slack_ready:
        raise SystemExit("Set SLACK_BOT_TOKEN and SLACK_APP_TOKEN in .env before running Slack mode.")
    agent = build_agent(config)
    SocketModeHandler(build_app(config, agent), config.slack_app_token).start()


if __name__ == "__main__":
    main()
