"""Slack Socket Mode app: the Agent surface, channel mentions, and a slash command.

Slack's Agent messaging experience (agent_view) replaced the older Assistant one:
`app_home_opened` + `app_context_changed` stand in for `assistant_thread_started` +
`assistant_thread_context_changed`, and agent DMs behave like ordinary messages.
Bolt's `Assistant` container is built for the legacy events, so the handlers below
are wired directly instead.
"""

from __future__ import annotations

import logging

from slack_bolt import App
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
    """Wire a model to the MCP server, or fall back to the deterministic router."""
    if not config.reasoning_ready:
        log.warning(
            "No ANTHROPIC_API_KEY or XAI_API_KEY (or LABSIGNAL_FORCE_LOCAL=1). "
            "Running the rule-based fallback; the model and MCP are disabled."
        )
        return LabSignalAgent()

    mcp = MCPToolSession()
    mcp.start()

    if config.provider == "anthropic":
        brain = ClaudeBrain(mcp, config.api_key, config.model)
    else:
        from .brain_grok import GrokBrain

        brain = GrokBrain(mcp, config.api_key, config.model)

    log.info(
        "%s (%s) reasoning over MCP tools: %s",
        config.provider,
        config.model,
        mcp.tool_names(),
    )
    return LabSignalAgent(brain)


def build_app(config: Config, agent: LabSignalAgent) -> App:
    app = App(token=config.slack_bot_token)

    # Which channel each user was looking at when they opened the agent. Slack sends
    # this separately from the message, and it is what lets read_slack_channel know
    # which conversation "this channel" refers to.
    channel_context: dict[str, str] = {}

    @app.event("app_context_changed")
    def remember_context(event, logger):
        context = event.get("context") or {}
        user_id = event.get("user") or context.get("user_id")
        channel_id = context.get("channel_id")
        if user_id and channel_id:
            channel_context[user_id] = channel_id
            logger.info("context: %s is looking at %s", user_id, channel_id)

    @app.event("app_home_opened")
    def greet(event, client, logger):
        if event.get("tab") != "messages":
            return  # the Home tab is a different surface; only greet in Messages
        channel_id = event.get("channel")
        if not channel_id:
            return
        client.chat_postMessage(channel=channel_id, text=GREETING)
        try:
            client.assistant_threads_setSuggestedPrompts(
                channel_id=channel_id,
                thread_ts=event.get("event_ts"),
                prompts=SUGGESTED_PROMPTS,
            )
        except Exception as error:
            # Cosmetic only -- the agent is fully usable by typing. Never let this
            # take the app down.
            logger.warning("could not set suggested prompts: %s", error)

    @app.event("message")
    def handle_dm(event, client, say, logger):
        # Agent DMs arrive as ordinary messages under agent_view.
        if event.get("channel_type") != "im":
            return
        if event.get("bot_id") or event.get("subtype"):
            return  # never answer ourselves

        thread_ts = event.get("thread_ts") or event.get("ts")
        try:
            client.assistant_threads_setStatus(
                channel_id=event["channel"],
                thread_ts=thread_ts,
                status="is reading the lab's Slack...",
            )
        except Exception:
            pass  # status is a nicety, not a requirement

        user_channel = channel_context.get(event.get("user", ""))
        text, tools_used = agent.respond(event.get("text", ""), user_channel)
        say(text=_fallback(text), blocks=answer_blocks(text, tools_used), thread_ts=thread_ts)

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
