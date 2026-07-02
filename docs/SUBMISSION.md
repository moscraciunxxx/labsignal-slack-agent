# Slack Agent Builder Challenge submission draft

## Track

New Slack Agent

## Project title

LabSignal: A Slack Research Ops Agent with MCP Tools

## Short description

LabSignal turns messy neuroscience research updates in Slack into structured lab
handoffs, summaries, action items, risk flags, experiment checklists, and
protocol lookups through a Slack bot backed by an MCP-compatible tool server.

## Long description

Research teams already coordinate experiments, analysis decisions, lab meeting
notes, and protocol questions in Slack. LabSignal makes those channels more
actionable. A researcher can mention the agent or use `/labsignal` to build a
research brief, summarize an update, extract owner/task/deadline action items,
flag QC and reproducibility risks, generate experiment checklists, or search a
small local neuroscience protocol knowledge base.

The project uses Slack Bolt for Python with Socket Mode, which makes the demo
easy to run inside the required Slack developer sandbox without paid hosting.
Its tools are also exposed through an MCP-compatible server:
`search_protocols`, `extract_action_items`, `summarize_update`,
`detect_risks`, `build_research_brief`, and `plan_experiment`.

## Required technology

Primary: MCP server integration

Slack surface: app mentions and `/labsignal` command in a Slack developer
sandbox.

## Demo script

1. Show the Slack sandbox and LabSignal installed.
2. Run `/labsignal brief Alice will QC CA1 Neuropixels recordings by Friday. Two channels are saturated and the session may need a re-run. Bob should update the SOP before next week.`
3. Show the structured summary, actions, risks, and relevant protocol.
4. Run `/labsignal plan ca1 neuropixels qc`.
5. Show the checklist, then run `/labsignal protocol ca1 neuropixels`.
6. Explain the MCP tools.
7. Close with the value: Slack-native research coordination that saves teams
   from losing action items and protocol context.

## No-spend path

This project requires only a free Slack developer sandbox. It runs locally with
Socket Mode and deterministic local tools, so no paid LLM or cloud service is
required for the core demo.
