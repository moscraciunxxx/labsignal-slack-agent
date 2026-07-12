# LabSignal

**New Slack Agent** for the Slack Agent Builder Challenge.
Primary technology: **MCP server integration**.

Research labs make decisions in Slack and lose them there. A recording session goes
sideways at 11pm, three people discuss it across two channels, and the next shift
walks in with no idea which channels were saturated, who agreed to re-run the QC, or
which SOP applies.

LabSignal reads that conversation and gives back the handoff.

> **@LabSignal** catch me up on the CA1 session
>
> *Two of Alice's CA1 Neuropixels channels saturated on Tuesday and she flagged the
> session for a possible re-run. Bob owes an SOP update before next week.*
>
> *Risks: signal quality (saturation — QC before spike sorting); schedule (re-run not
> yet scheduled).*
>
> *Relevant protocol: CA1 Neuropixels QC (`ca1-neuropixels-qc`).*
>
> 🔌 *via MCP: `read_slack_channel`, `build_research_brief`*

## How MCP is load-bearing

LabSignal has no hardcoded command router in its main path. The Slack app is an **MCP
client**: at startup it spawns `labsignal.mcp_server` over stdio, discovers the tool
schemas, and hands them to Claude, which decides what to call and in what order.
Remove the MCP server and the agent has no capabilities at all.

That is what lets a researcher ask a question in their own words instead of learning a
command grammar. "Who still owes me something on the CA1 session?" makes Claude call
`read_slack_channel` and then `extract_action_items` — a chain nobody wrote by hand.

Tools exposed over MCP:

| Tool | What Claude uses it for |
| --- | --- |
| `read_slack_channel` | Pull the real conversation instead of asking the user to paste it |
| `build_research_brief` | Compose a full handoff: summary, actions, risks, protocols |
| `extract_action_items` | Owner / task / deadline triples |
| `detect_risks` | QC, schedule, governance, and reproducibility flags |
| `search_protocols` | The lab's protocol knowledge base |
| `plan_experiment` | Pre-session checklists |
| `summarize_update` | Compress a long update to its leading claim |

Every reply is footed with the MCP tools that produced it, so you can see the agent's
reasoning path rather than trust it.

## Slack-native surface

- **Assistant pane** — LabSignal appears in Slack's AI assistant surface with suggested
  prompts and a live "is reading the lab's Slack…" status while it works.
- **`@LabSignal`** in any channel — replies in-thread so it never derails the discussion.
- **`/labsignal`** for a quick shared answer.
- Replies render as **Block Kit**, not raw text.

## Grounding

The agent is instructed that it knows nothing about the lab except what its tools
return, and must never invent an owner, deadline, session ID, or protocol step. When a
tool comes back empty it says so. `read_slack_channel` fails loudly if the bot was
never invited to the channel rather than guessing at content.

## Quickstart

```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env    # add SLACK_BOT_TOKEN, SLACK_APP_TOKEN, ANTHROPIC_API_KEY

$env:PYTHONPATH="src"
python -m labsignal.slack_app
```

Try the agent loop without Slack — this spawns the MCP server and runs the same
Claude tool-selection path the Slack app uses:

```bash
python -m labsignal.cli "Alice will QC CA1 Neuropixels recordings by Friday. Two channels are saturated. What should the next shift know?" --verbose
python -m labsignal.cli "who owes what on the CA1 session?" --channel C0123456789
```

## Running without an Anthropic key

If `ANTHROPIC_API_KEY` is unset, LabSignal degrades to a deterministic keyword router
(`brief`, `actions`, `risks`, `plan`, `protocol`, `summarize`). It still answers and
costs nothing, but it cannot handle plain-English questions or chain tools — that is
the part Claude and MCP do.

## Tests

```bash
$env:PYTHONPATH="src"
python -m pytest tests -q
```

The suite spawns the real MCP server over stdio and round-trips a tool call through
it, so the integration is covered rather than mocked.

## Docker

```bash
docker build -t labsignal .
docker run --rm --env-file .env labsignal
```

See `docs/ARCHITECTURE.md` for the architecture diagram.
