"""Local CLI: exercises the same Claude-over-MCP path the Slack app uses, without Slack."""

from __future__ import annotations

import argparse
import logging

from .config import Config


def main() -> None:
    parser = argparse.ArgumentParser(description="Ask LabSignal a question from the terminal.")
    parser.add_argument("message")
    parser.add_argument("--channel", help="Slack channel ID to let the agent read", default=None)
    parser.add_argument("--verbose", action="store_true", help="Log MCP and tool activity")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO if args.verbose else logging.WARNING)

    # Imported here so the fallback path stays importable without slack_bolt installed.
    from .slack_app import build_agent

    config = Config()
    agent = build_agent(config)
    text, tools_used = agent.respond(args.message, args.channel)

    print(text)
    if tools_used:
        print(f"\n[MCP tools called: {', '.join(tools_used)}]")
    elif agent.is_reasoning:
        print("\n[MCP tools called: none]")


if __name__ == "__main__":
    main()
