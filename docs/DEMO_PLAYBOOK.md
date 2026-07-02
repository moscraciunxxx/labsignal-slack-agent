# LabSignal demo playbook

Target length: 2:30 to 3:00.

## Judge-facing thesis

LabSignal is a Slack-native research operations agent for neuroscience teams. It
turns messy lab-channel messages into structured action items, protocol lookups,
and concise updates using a Slack bot backed by MCP-compatible tools.

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
   $env:PYTHONPATH="src"
   python -m labsignal.slack_app
   ```

2. Keep a terminal tab ready with:

   ```powershell
   python -m labsignal.mcp_server
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

### 0:20-0:55 - Action extraction

Paste:

```text
/labsignal actions Alice will QC CA1 Neuropixels recordings by Friday. Bob should update the SOP before next week. Maya needs to export rejected channel IDs today.
```

Say:

"The agent extracts owners, tasks, and deadlines directly from ordinary lab
messages."

### 0:55-1:25 - Protocol lookup

Paste:

```text
/labsignal protocol ca1 neuropixels qc
```

Say:

"It can also surface protocol knowledge. This is implemented as a local tool,
which is the same capability exposed through the MCP server."

### 1:25-1:55 - Summary flow

Paste:

```text
/labsignal summarize Today we finished CA1 recordings for cohort B. Two probes had saturated channels and one session needs re-running. Alice will QC the recordings by Friday, and Bob will update the SOP before next week.
```

Say:

"For noisy status updates, the agent gives a concise summary so the channel
stays usable."

### 1:55-2:25 - Technical proof

Show:

- `src/labsignal/slack_app.py` for Slack Bolt Socket Mode.
- `src/labsignal/mcp_server.py` for MCP tools.
- `docs/slack-app-manifest.yaml` for app scopes and event setup.

Say:

"The Slack surface is app mentions and slash commands. The reusable tool layer is
also exposed as MCP: search protocols, extract action items, and summarize
updates."

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

