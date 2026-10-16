# One long Claude Code session was 39% cheaper than starting fresh every task

*Draft. Tech in General experiment #019. 20 headless Claude Code turns (Opus 5.5, Pro), 2026-10-15 IST.*

Common advice: `/clear` between tasks so you aren't paying for old context. I fixed 10 small packages two ways: one session resumed for every task, or a brand-new session per task.

| | One long session | Fresh per task |
|---|---|---|
| Fixed | 10/10 | 10/10 |
| Tokens sent | 921K | 571K |
| Est. cost | **55¢** | 91¢ |

The long session sent 61% more tokens and still cost less.

**Why.** Claude Code caches the conversation for an hour. Writing to that cache costs 2× the normal input price; reading it costs 1/20th. A fresh session has to write 7–13K tokens of new context every time. The long session only writes the newest turn and re-reads the rest at cache price. Its context did grow (16K → 38K tokens by task 10), but cheap reads beat expensive writes.

**When this flips.** If tasks are more than an hour apart (cache expires), if the session gets big enough to compact, or if old context starts confusing the model. None of that happened in 10 quick tasks.

**Takeaway.** For a batch of related small tasks done back to back, keep the session. Clear it when you switch topics or take a break.

*$ are API-equivalent estimates from Claude Code's usage numbers; Pro isn't billed per token. Note: in a resumed headless session `total_cost_usd` is cumulative, so subtract the previous turn's figure.*
