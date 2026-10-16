# #019 Fresh session per task vs one long session (Claude Code CLI)

**Question.** Fixing 10 packages in one repo: is it cheaper to keep one Claude Code session going (`claude -p --resume <id>` per task) or start a fresh session per task?

**Short answer.** The opposite of what you'd guess. The long session sent **61% more tokens** (921K vs 571K) and its starting prompt grew from 16.5K to 37.6K tokens, yet it was **39% cheaper** in API-equivalent cost (**$0.55 vs $0.91** for 10 tasks). Both arms fixed **10/10**. Reason: Claude Code writes to the 1-hour prompt cache at $8/M and reads it at $0.20/M. Each fresh session wrote 7–13K new tokens to cache (≈$0.06–0.10 of cache writes per task); the long session only wrote the new turn (1–3.6K) and re-read its growing history at 1/40 the price. Per task after the first, the long session cost $0.035–0.063 vs $0.071–0.139 fresh. No mistakes or cross-task confusion showed up in the long session over 10 tasks.

## Setup
- Claude Code 2.1.300, `claude-opus-5-5`, default effort, Pro sign-in; headless `claude -p … --output-format stream-json --verbose --dangerously-skip-permissions --strict-mcp-config`.
- Same design as the Codex chain experiments (`_harness/chain.sh`): one copy of `SUITE14`, the first 10 packages in order (N01_median … T07_multihunk), one per turn, prompt "Make `node test.js` pass inside the package folder `<pkg>/` … Only work on <pkg>/ in this turn." Pass per turn = `cd <pkg> && node test.js` and no test.js changed.
  - **long**: turn 1 `claude -p`, turns 2–10 `claude -p --resume <session_id>`.
  - **fresh**: a new `claude -p` per turn in the same directory (so later turns see earlier fixes on disk).
- 1 chain per arm, both run at the same time, 2026-10-14 ~19:57–20:00 UTC.
- **Cost accounting:** in a resumed session, Claude Code's `total_cost_usd` (and `modelUsage`) is *cumulative for the session*, while `usage` is per turn. Per-turn cost for the long arm = difference of consecutive cumulative costs (`scripts/analyze.py`). Est. $ is the list-API price — **API-equivalent estimate; Pro isn't billed per token.**

## Exact commands
```bash
source /workspace/tools/setup.sh
scripts/run_all.sh 1        # runs scripts/harness/chain_cc.sh for both arms in parallel
/workspace/tools/mlenv/bin/python scripts/analyze.py
```

## Results (10 tasks per arm)
| Arm | Passed | Total tokens | Cache write | Cache read | Output | Prompt at task 10 | Est. $ | Wall |
|---|---|---|---|---|---|---|---|---|
| long (resumed) | 10/10 | 920,725 | 30,418 | 883,555 | 6,692 | 37,615 | **$0.554** | 108 s |
| fresh per task | 10/10 | 571,180 | 88,929 | 477,044 | 5,145 | 16,503 | $0.910 | 97 s |

Per-turn numbers: `results/per_turn.csv`. Chart: `results/chart.png` (prompt size per task; cumulative cost).

## Caveats
- One chain per arm (Claude's run-to-run variance was ~1% in #010b, so the gap is well outside noise, but it's one ordering of one task set).
- Small tasks. The long session's context grew ~2K tokens per task; at 100+ tasks or with big tool outputs the cache-read cost and context pressure (and eventually auto-compaction) would eat the advantage. The crossover isn't measured here.
- The 1-hour cache TTL matters: tasks spaced more than an hour apart would make the long session pay cache writes again.
- "Mistakes" = failed tasks or touching other packages' tests; none in either arm. I didn't grade code quality.
