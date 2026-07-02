# Slack Agent Builder Challenge submission draft

## Track

New Slack Agent

## Project title

LabSignal: A Slack Research Ops Agent with MCP Tools

## Short description

LabSignal turns messy neuroscience research updates in Slack into summaries,
action items, and protocol lookups through a Slack bot backed by an
MCP-compatible tool server.

## Long description

Research teams already coordinate experiments, analysis decisions, lab meeting
notes, and protocol questions in Slack. LabSignal makes those channels more
actionable. A researcher can mention the agent or use `/labsignal` to summarize
an update, extract owner/task/deadline action items, or search a small local
neuroscience protocol knowledge base.

The project uses Slack Bolt for Python with Socket Mode, which makes the demo
easy to run inside the required Slack developer sandbox without paid hosting.
Its tools are also exposed through an MCP-compatible server:
`search_protocols`, `extract_action_items`, and `summarize_update`.

## Required technology

Primary: MCP server integration

Slack surface: app mentions and `/labsignal` command in a Slack developer
sandbox.

## Demo script

1. Show the Slack sandbox and LabSignal installed.
2. Mention the bot with: `@LabSignal actions Alice will QC CA1 recordings by Friday. Bob should update the SOP.`
3. Show the structured action items.
4. Run `/labsignal protocol ca1 neuropixels`.
5. Show the matching local protocol and explain the MCP tools.
6. Run `/labsignal summarize ...` on a messy lab update.
7. Close with the value: Slack-native research coordination that saves teams
   from losing action items and protocol context.

## No-spend path

This project requires only a free Slack developer sandbox. It runs locally with
Socket Mode and deterministic local tools, so no paid LLM or cloud service is
required for the core demo.

