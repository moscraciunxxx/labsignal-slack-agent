"""Environment configuration.

LabSignal can reason with either Claude or Grok. The choice does not touch the
architecture: whichever model runs, its tools are still discovered from the MCP
server and it still decides what to call.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field

try:
    from dotenv import load_dotenv

    load_dotenv()
except Exception:
    pass

DEFAULT_CLAUDE_MODEL = "claude-opus-4-8"
DEFAULT_GROK_MODEL = "grok-4.3"


def _get(name: str, default: str = "") -> str:
    value = os.environ.get(name)
    return value if value not in (None, "") else default


@dataclass
class Config:
    slack_bot_token: str = field(default_factory=lambda: _get("SLACK_BOT_TOKEN"))
    slack_app_token: str = field(default_factory=lambda: _get("SLACK_APP_TOKEN"))
    anthropic_api_key: str = field(default_factory=lambda: _get("ANTHROPIC_API_KEY"))
    # XAI_API_KEY is xAI's own name for it; GROK_API_KEY is accepted as a convenience.
    xai_api_key: str = field(
        default_factory=lambda: _get("XAI_API_KEY") or _get("GROK_API_KEY")
    )
    model_override: str = field(default_factory=lambda: _get("LABSIGNAL_MODEL"))
    provider_override: str = field(
        default_factory=lambda: _get("LABSIGNAL_PROVIDER").strip().lower()
    )
    force_local: bool = field(
        default_factory=lambda: _get("LABSIGNAL_FORCE_LOCAL", "0").lower() in {"1", "true", "yes"}
    )

    @property
    def slack_ready(self) -> bool:
        return bool(self.slack_bot_token and self.slack_app_token)

    @property
    def provider(self) -> str:
        """'anthropic', 'xai', or 'none' -- whichever key is present."""
        if self.force_local:
            return "none"
        if self.provider_override in {"anthropic", "xai"}:
            return self.provider_override
        if self.anthropic_api_key:
            return "anthropic"
        if self.xai_api_key:
            return "xai"
        return "none"

    @property
    def api_key(self) -> str:
        return self.anthropic_api_key if self.provider == "anthropic" else self.xai_api_key

    @property
    def model(self) -> str:
        if self.model_override:
            return self.model_override
        return DEFAULT_CLAUDE_MODEL if self.provider == "anthropic" else DEFAULT_GROK_MODEL

    @property
    def reasoning_ready(self) -> bool:
        """True when LabSignal can run the model-over-MCP loop instead of the fallback."""
        return self.provider != "none" and bool(self.api_key)
