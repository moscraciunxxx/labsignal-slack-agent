"""Read Slack conversation history on behalf of the MCP server."""

from __future__ import annotations

from datetime import datetime, timezone

MAX_LIMIT = 200


def fetch_channel_messages(
    bot_token: str, channel_id: str, limit: int = 40
) -> list[dict[str, str]]:
    """Return recent human messages from a channel, oldest first."""
    if not bot_token:
        raise RuntimeError("SLACK_BOT_TOKEN is not set, so Slack history is unavailable.")

    from slack_sdk import WebClient
    from slack_sdk.errors import SlackApiError

    client = WebClient(token=bot_token)
    limit = max(1, min(limit, MAX_LIMIT))

    try:
        response = client.conversations_history(channel=channel_id, limit=limit)
    except SlackApiError as error:
        code = error.response.get("error", "unknown_error")
        if code == "not_in_channel":
            raise RuntimeError(
                f"LabSignal is not a member of {channel_id}. Invite it with /invite @LabSignal."
            ) from error
        raise RuntimeError(f"Slack rejected the history request for {channel_id}: {code}") from error

    names: dict[str, str] = {}
    messages: list[dict[str, str]] = []
    for message in reversed(response.get("messages", [])):
        text = (message.get("text") or "").strip()
        if not text or message.get("subtype"):
            continue
        user_id = message.get("user") or message.get("bot_id") or ""
        messages.append(
            {
                "author": _display_name(client, user_id, names),
                "at": _iso(message.get("ts", "")),
                "text": text,
            }
        )
    return messages


def _display_name(client, user_id: str, cache: dict[str, str]) -> str:
    if not user_id:
        return "unknown"
    if user_id not in cache:
        try:
            profile = client.users_info(user=user_id)["user"]
            cache[user_id] = profile.get("real_name") or profile.get("name") or user_id
        except Exception:
            cache[user_id] = user_id
    return cache[user_id]


def _iso(ts: str) -> str:
    try:
        return datetime.fromtimestamp(float(ts), tz=timezone.utc).isoformat(timespec="seconds")
    except (TypeError, ValueError):
        return ts
