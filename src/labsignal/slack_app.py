"""Slack Bolt Socket Mode app."""

from __future__ import annotations

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

from .agent import LabSignalAgent
from .config import Config

config = Config()
agent = LabSignalAgent()

app = App(token=config.slack_bot_token)


@app.event("app_mention")
def handle_mention(event, say):
    say(agent.respond(event.get("text", "")))


@app.command("/labsignal")
def handle_command(ack, respond, command):
    ack()
    respond(agent.respond(command.get("text", "")))


def main() -> None:
    if not config.slack_ready:
        raise SystemExit("Set SLACK_BOT_TOKEN and SLACK_APP_TOKEN in .env before running Slack mode.")
    SocketModeHandler(app, config.slack_app_token).start()


if __name__ == "__main__":
    main()

