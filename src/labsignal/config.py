"""Environment configuration."""

from __future__ import annotations

import os
from dataclasses import dataclass, field

try:
    from dotenv import load_dotenv

    load_dotenv()
except Exception:
    pass

DEFAULT_MODEL = "claude-opus-4-8"


def _get(name: str, default: str = "") -> str:
    value = os.environ.get(name)
    return value if value not in (None, "") else default


@dataclass
class Config:
    slack_bot_token: str = field(default_factory=lambda: _get("SLACK_BOT_TOKEN"))
    slack_app_token: str = field(default_factory=lambda: _get("SLACK_APP_TOKEN"))
    anthropic_api_key: str = field(default_factory=lambda: _get("ANTHROPIC_API_KEY"))
    model: str = field(default_factory=lambda: _get("LABSIGNAL_MODEL", DEFAULT_MODEL))
    force_local: bool = field(
        default_factory=lambda: _get("LABSIGNAL_FORCE_LOCAL", "0").lower() in {"1", "true", "yes"}
    )

    @property
    def slack_ready(self) -> bool:
        return bool(self.slack_bot_token and self.slack_app_token)

    @property
    def reasoning_ready(self) -> bool:
        """True when LabSignal can run the Claude-over-MCP loop instead of the fallback."""
        return bool(self.anthropic_api_key) and not self.force_local
