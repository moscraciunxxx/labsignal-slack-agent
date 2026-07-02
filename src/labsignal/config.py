"""Environment configuration."""

from __future__ import annotations

import os
from dataclasses import dataclass, field

try:
    from dotenv import load_dotenv

    load_dotenv()
except Exception:
    pass


def _get(name: str, default: str = "") -> str:
    value = os.environ.get(name)
    return value if value not in (None, "") else default


@dataclass
class Config:
    slack_bot_token: str = field(default_factory=lambda: _get("SLACK_BOT_TOKEN"))
    slack_app_token: str = field(default_factory=lambda: _get("SLACK_APP_TOKEN"))
    force_local: bool = field(
        default_factory=lambda: _get("LABSIGNAL_FORCE_LOCAL", "1").lower() in {"1", "true", "yes"}
    )

    @property
    def slack_ready(self) -> bool:
        return bool(self.slack_bot_token and self.slack_app_token)

