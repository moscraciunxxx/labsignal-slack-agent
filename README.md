# LabSignal

**New Slack Agent** for the Slack Agent Builder Challenge.

LabSignal helps neuroscience and research teams turn scattered Slack messages
into concrete next steps. It builds lab handoffs, answers protocol questions,
extracts action items, flags risks, and summarizes research updates through a
Slack bot backed by an MCP-compatible local tool server.

## Why This Competition

This project is designed for the no-spend path:

- Uses a free Slack Developer Program sandbox.
- Runs locally with Slack Socket Mode, so no paid deployment is needed for early
  demos.
- Uses local deterministic tools by default.
- Adds an MCP-compatible server to satisfy the hackathon technology requirement
  without requiring paid LLM/API calls.

## Features

- `@LabSignal summarize ...` creates concise research summaries.
- `@LabSignal actions ...` extracts owners, tasks, and deadlines.
- `@LabSignal brief ...` creates a structured lab handoff with summary, actions,
  risks, and relevant protocols.
- `@LabSignal risks ...` flags QC, schedule, governance, and reproducibility
  risks.
- `@LabSignal plan ca1 neuropixels qc` returns a workflow checklist.
- `@LabSignal protocol ca1 recording` searches a small neuroscience protocol
  knowledge base.
- `/labsignal` slash command support for fast demos.
- MCP tools in `src/labsignal/mcp_server.py`.

## Quickstart

```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env

$env:PYTHONPATH="src"
python -m labsignal.cli "actions Alice will QC CA1 recordings by Friday. Bob should update the protocol."
python -m labsignal.cli "brief Alice will QC CA1 Neuropixels recordings by Friday. Two channels are saturated."
python -m labsignal.cli "plan ca1 neuropixels qc"
python -m labsignal.cli "protocol ca1 neuropixels"
```

## Slack Setup

1. Join the Slack Agent Builder Challenge on Devpost.
2. Join the Slack Developer Program and provision the free developer sandbox.
3. Use the hackathon sandbox code from the FAQ: `SABC-7X2K-M9PL-4QFN`.
4. Create a Slack app in the sandbox.
5. Enable Socket Mode.
6. Add bot scopes:
   - `app_mentions:read`
   - `chat:write`
   - `commands`
7. Add a slash command:
   - Command: `/labsignal`
   - Request URL: any placeholder URL if Socket Mode is enabled
8. Install the app to the sandbox.
9. Put tokens in `.env`:

```env
SLACK_BOT_TOKEN=xoxb-your-token
SLACK_APP_TOKEN=xapp-your-token
```

Run the bot:

```bash
$env:PYTHONPATH="src"
python -m labsignal.slack_app
```

## MCP Server

```bash
$env:PYTHONPATH="src"
python -m labsignal.mcp_server
```

Exposed tools:

- `search_protocols`
- `extract_action_items`
- `summarize_update`
- `detect_risks`
- `build_research_brief`
- `plan_experiment`

## Docker

```bash
docker build -t labsignal .
docker run --rm --env-file .env labsignal
```

## Submission Plan

Track: **New Slack Agent**

Primary technology: **MCP server integration**

See `docs/SUBMISSION.md` for the Devpost draft, `docs/DEMO_PLAYBOOK.md` for the
recording script, and `docs/ARCHITECTURE.md` for the architecture diagram.
