"""Block Kit rendering for LabSignal replies."""

from __future__ import annotations

SECTION_LIMIT = 2900  # Slack caps a section's text at 3000 characters.


def answer_blocks(text: str, tools_used: list[str] | None = None) -> list[dict]:
    """Render an answer, footed by the MCP tools that produced it."""
    blocks: list[dict] = [
        {"type": "section", "text": {"type": "mrkdwn", "text": chunk}}
        for chunk in _chunk(text)
    ]
    if tools_used:
        blocks.append(
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": "🔌 via MCP: " + ", ".join(f"`{name}`" for name in tools_used),
                    }
                ],
            }
        )
    return blocks


def _chunk(text: str) -> list[str]:
    text = text.strip() or "_(no response)_"
    chunks: list[str] = []
    while len(text) > SECTION_LIMIT:
        split = text.rfind("\n", 0, SECTION_LIMIT)
        if split <= 0:
            split = SECTION_LIMIT
        chunks.append(text[:split].strip())
        text = text[split:].strip()
    chunks.append(text)
    return chunks
