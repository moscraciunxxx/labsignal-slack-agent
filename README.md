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
- `@LabSignal demo` shows a polished judge-facing command menu.
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
python -m labsignal.cli "demo"
```



## Docker

```bash
docker build -t labsignal .
docker run --rm --env-file .env labsignal
```


Primary technology: **MCP server integration**

See `docs/ARCHITECTURE.md` for the architecture diagram.
