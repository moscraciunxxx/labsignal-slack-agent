"""Local CLI for demos without Slack credentials."""

from __future__ import annotations

import argparse

from .agent import LabSignalAgent


def main() -> None:
    parser = argparse.ArgumentParser(description="Run LabSignal locally.")
    parser.add_argument("message")
    args = parser.parse_args()
    print(LabSignalAgent().respond(args.message))


if __name__ == "__main__":
    main()

