# LabSignal demo playbook

Target length: 2:30 to 3:00.

## Judge-facing thesis

LabSignal is a Slack-native research operations agent for neuroscience teams. It
turns messy lab-channel messages into structured handoffs, action items, risk
flags, experiment plans, protocol lookups, and concise updates using a Slack bot
backed by MCP-compatible tools.

## What judges score

- Technological implementation: working Slack app, quality code, and at least
  one required technology. LabSignal uses MCP server integration.
- Design: Slack-native interaction, useful outputs, low-friction UX, and a
  balanced backend/tooling story.
- Potential impact: fewer lost lab tasks, faster protocol recall, better
  coordination for research teams.
- Quality of idea: focused agent for a real operational pain point rather than a
  generic chatbot.

## Recording setup

Before recording:

1. Start the bot:

   ```powershell
   cd "D:\Coding Compete\2026-07-13_Slack-Agent-Builder-Challenge"
   $py="C:\Users\moscr\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
   $env:PYTHONPATH="src"
   & $py -m labsignal.slack_app
   ```

2. Keep a terminal tab ready with:

   ```powershell
   cd "D:\Coding Compete\2026-07-13_Slack-Agent-Builder-Challenge"
   $py="C:\Users\moscr\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
   $env:PYTHONPATH="src"
   & $py -m labsignal.mcp_server
   ```

3. Open Slack to `#general`.
4. Open the GitHub repo or local README in another tab.
5. Hide tokens, `.env`, personal notifications, and unrelated browser tabs.
6. Increase browser zoom to 110% or 125% so Slack text reads well on video.

## Demo script

### 0:00-0:20 - Problem

"Research teams already coordinate experiments, analysis decisions, lab meeting
notes, and protocol questions in Slack. The problem is that action items and
protocol context get buried. LabSignal turns those messages into structured
research operations support without leaving Slack."

### 0:20-0:55 - Research brief

Paste:

```text
/labsignal brief Alice will QC CA1 Neuropixels recordings by Friday. Two channels are saturated and the session may need a re-run. Bob should update the SOP before next week. Maya needs to export rejected channel IDs today.
```

Say:

"The agent turns an ordinary lab update into a research handoff: summary,
actions, risk flags, and relevant protocols."

### 0:55-1:20 - Experiment planning

Paste:

```text
/labsignal plan ca1 neuropixels qc
```

Say:

"It can generate workflow checklists for common neuroscience operations, keeping
the next steps inside Slack."

### 1:20-1:45 - Protocol lookup

Paste:

```text
/labsignal protocol ca1 neuropixels qc
```

Say:

"It also surfaces protocol knowledge. These are deterministic tools, and the
same capabilities are exposed through the MCP server."

### 1:55-2:25 - Technical proof

Show:

- `src/labsignal/slack_app.py` for Slack Bolt Socket Mode.
- `src/labsignal/mcp_server.py` for MCP tools.
- `docs/slack-app-manifest.yaml` for app scopes and event setup.

Say:

"The Slack surface is app mentions and slash commands. The reusable tool layer is
also exposed as MCP: search protocols, extract action items, summarize updates,
detect risks, build briefs, and plan experiments."

### 2:25-2:55 - Impact and close

"LabSignal is intentionally small and shippable: it helps research teams reduce
lost tasks, standardize protocol recall, and keep Slack as the actual work
surface. The same pattern could be extended to electronic lab notebooks, issue
trackers, or institutional knowledge bases."

## Best screenshots

- Slack channel showing all three commands and responses.
- App configuration showing the sandbox app name and installed bot.
- Short code screenshot of MCP tool definitions.
- Architecture diagram, if added.

## Avoid

- Do not show token pages or `.env`.
- Do not spend time explaining setup forms.
- Do not show repeated duplicate test messages.
- Do not claim LLM reasoning if the current implementation is deterministic.
