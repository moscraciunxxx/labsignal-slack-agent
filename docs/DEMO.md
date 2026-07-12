# Demo script (~3 minutes)

Judges spend 5–7 minutes per project. The first 60 seconds must show the agent doing
something a keyword bot could not, and must show MCP doing real work.

## Before recording

1. `.env` has `SLACK_BOT_TOKEN`, `SLACK_APP_TOKEN`, `ANTHROPIC_API_KEY`.
2. The app is installed from `docs/slack-app-manifest.yaml` (the Assistant pane and
   `channels:history` scope come from the new manifest — an older install will not
   have them).
3. `/invite @LabSignal` in the demo channel, or `read_slack_channel` will refuse.
4. Seed `#ca1-recordings` with a messy, realistic thread — no keywords, no structure:

   > **Alice** — rig 2 is being weird tonight, ch 47 and 51 look saturated again
   > **Bob** — same as last week? if it's the same two we should probably re-run
   > **Alice** — yeah. i'll QC the whole session properly on Friday before anyone sorts it
   > **Priya** — don't spike-sort until she's done pls
   > **Bob** — also our SOP still says the old probe map, i'll fix it before next week

5. Dry-run once: `python -m labsignal.cli "..." --verbose` and confirm you see
   `[MCP tools called: ...]`.

## Beat 1 (0:00–0:20) — the problem, in one line

"Labs make decisions in Slack and lose them there. A recording goes sideways at 11pm,
three people discuss it, and the next shift walks in blind."

Show the seeded channel scrolling. It looks like every real lab channel: no structure.

## Beat 2 (0:20–1:10) — the agent, in plain English

Open the **Assistant pane**. Show the suggested prompts, then type something that is
deliberately *not* a command:

> catch me up on the CA1 session

Let the "is reading the lab's Slack…" status show. Then the reply lands: Alice's two
saturated channels, the re-run decision, Bob's SOP update, the QC risk, the matching
protocol — with the footer:

> 🔌 via MCP: `read_slack_channel`, `build_research_brief`

**Say this out loud:** "I never told it to read the channel. It decided to."

## Beat 3 (1:10–1:50) — prove MCP is load-bearing

Cut to the terminal. Show the startup line:

```
Claude (claude-opus-4-8) reasoning over MCP tools:
['read_slack_channel', 'search_protocols', 'extract_action_items', ...]
```

"The Slack app imports no tool module. That tool list is discovered at runtime by
calling `list_tools()` on the MCP server. Remove the server and the agent still gets
Slack messages, still calls Claude — and can do nothing at all."

Optionally show the same server running in Claude Desktop: the lab's protocol search
is not locked inside a Slack bot.

## Beat 4 (1:50–2:30) — chaining, not routing

Back in Slack, ask a different question about the *same* channel:

> who still owes me something?

Footer now reads `read_slack_channel`, `extract_action_items` — a different chain, for
a different question, that nobody hardcoded. Then:

> is it safe to spike-sort this session yet?

It answers *no*, citing Priya's message and the QC risk. That is the payoff: it reasons
over the conversation instead of matching keywords.

## Beat 5 (2:30–3:00) — trust and impact

"It only knows what its tools return. It's instructed never to invent an owner, a
deadline, or a protocol step — and if the bot was never invited to a channel, it says
so instead of guessing."

Close on impact: every shift handoff, every 'who owes what', every 'is this data safe
to use' — answered from the lab's own Slack, in the lab's own words.

## Do not

- Do not demo the keyword fallback. It exists so the app degrades gracefully without
  an API key; it is not the product.
- Do not paste a research update into the command. Making the user paste the
  conversation is the thing this version fixed.
