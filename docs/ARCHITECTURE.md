# LabSignal architecture

LabSignal is an **MCP client** wrapped in a Slack app. The Slack layer transports
messages; Claude does the reasoning; every capability it has arrives over MCP.

```
  Slack workspace
  ├─ Assistant pane  ─┐
  ├─ @LabSignal       ├──▶  Slack Bolt (Socket Mode)
  └─ /labsignal      ─┘            │
                                   ▼
                            LabSignalAgent
                                   │
                                   ▼
                    Claude (claude-opus-4-8) tool-use loop
                                   │  picks tools, chains them, decides when to stop
                                   ▼
                    ══════ MCP stdio session ══════        ◀── the required technology
                                   │
                            labsignal.mcp_server
                                   │
        ┌──────────────┬───────────┼──────────────┬────────────────┐
        ▼              ▼           ▼              ▼                ▼
 read_slack_channel  build_    extract_       detect_risks    search_protocols
   (Slack Web API)   research_  action_items                  plan_experiment
                     brief                                    summarize_update
```

## Request flow

1. A researcher asks a question in the assistant pane, with `@LabSignal`, or via
   `/labsignal`. No command grammar — plain English.
2. Bolt hands the text and the channel ID to `LabSignalAgent`.
3. `ClaudeBrain` opens a Claude tool-use loop. The tool schemas were **discovered from
   the MCP server at startup**, not written into the prompt.
4. Claude chains tools as needed. "Catch me up on the CA1 session" typically becomes
   `read_slack_channel` → `build_research_brief`; "who owes what?" becomes
   `read_slack_channel` → `extract_action_items`.
5. Each call round-trips over the stdio MCP session to `labsignal.mcp_server`.
6. The answer is rendered as Block Kit and posted back in-thread, footed with the MCP
   tools that produced it.

## Why MCP is required, not decorative

The agent has **no direct import path to its tools**. `slack_app.py` imports no tool
module; `brain.py` builds its tool list by calling `list_tools()` on the MCP session.
Kill the MCP server and LabSignal can still receive a Slack message and still call
Claude — but Claude has zero tools and can do nothing. That is the dependency the
challenge asks for.

It also buys something real: because the tools are MCP-standard, the same server runs
unchanged in Claude Desktop or any MCP client. The lab's protocol search and QC risk
scan are not locked inside a Slack bot.

## Concurrency

Bolt's handlers are synchronous; the MCP session and the Anthropic tool loop are async
and must outlive any single request. `MCPToolSession` owns one background thread
running one event loop, opens the stdio session inside it once at startup, and Slack
handlers submit work to that loop with `asyncio.run_coroutine_threadsafe`.

## Degradation

Without `ANTHROPIC_API_KEY`, `build_agent` skips the MCP session entirely and returns a
`LabSignalAgent` with no brain, which falls back to a deterministic keyword router. The
same fallback catches any runtime failure in the Claude/MCP path, so a bad API call
downgrades the answer instead of dropping the message.
