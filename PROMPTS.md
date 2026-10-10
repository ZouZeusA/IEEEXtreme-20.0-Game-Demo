# Agent prompts for IEEEXtreme 20.0 game-type tasks (AI allowed)

Use these only on tasks the statement marks as game-type / AI-allowed.
On locked-workspace tasks, AI use is prohibited.

One person per lane. Each lane is one AI session (Claude Code, Cursor, ChatGPT,
Gemini, whatever your team uses). Lanes talk through files, not through chat:
`SPEC.md`, `referee.py`, `bots/`, `results.txt`.

---

## Lane 1: Spec agent (first 15 minutes, before anyone writes a bot)

```
Here is a game task statement: <paste statement>

Produce SPEC.md with exactly these sections:
1. Init input: every line, every field, type and range.
2. Per-turn input: every line, every field, type and range, in order.
3. Per-turn output: exact accepted strings and format. What counts as invalid.
4. Time limits: first turn and later turns. Memory limit. Max turns.
5. Win / lose / draw conditions, and what happens on timeout or invalid output.
6. Scoring: how the task is scored (vs fixed bots? vs other teams? per test?).
7. Ambiguities: every place the statement is unclear. Do NOT guess; list them.
Quote the statement for each rule you extract.
```

Human check: read section 7 out loud. Resolve ambiguities against the
statement's sample interaction, or ask the judges through the platform.

## Lane 2: Referee agent (builds the local test harness)

```
Using SPEC.md, write referee.py that:
- starts two bot commands as subprocesses and talks to them over stdin/stdout
- sends exactly the inputs in SPEC.md, in order
- enforces the per-turn time limit and kills a bot that times out
- rejects invalid output exactly as SPEC.md says
- has a --seed flag and a --show flag that prints the state each turn
- returns winner, number of turns, and the reason each bot died
Then write tournament.py: N games, swap sides every game, print win rate.
Write tests that replay the statement's sample interaction and check the
referee produces the same responses.
```

Human check: run the sample interaction. If the referee disagrees with the
statement even once, nothing else is trustworthy yet.

## Lane 3: Bot agent (builds the player, version by version)

```
Using SPEC.md, write bots/v0.py: the simplest bot that reads ALL input every
turn, never outputs an invalid move, flushes after every line, and never times
out. Print debug info to stderr only.
```
Then, one change per version:
```
Here are tournament results for bots/vN.py: <paste results, including how it died>.
Propose ONE change that addresses the most common death reason.
Write it as bots/vN+1.py. Explain in 3 lines why it should help.
```

Human check: every new version must beat the previous version AND not get
worse against the rest of the pool (run gauntlet.py). Keep the version that
wins; delete the story about why it should have won.

## Lane 4: Adversary / reviewer agent

```
Read bots/vN.py and SPEC.md.
1. Write 2 opponent bots with different styles than vN (e.g. aggressive
   chaser, wall-hugger) and save them in bots/.
2. List every way vN can time out or desync: unread input lines, missing
   flush, slow loops on the largest board, recursion depth, exceptions.
3. Estimate the worst-case time per turn on the largest input in SPEC.md.
```

Human check: run the largest board with timing on. If the worst turn is above
half the time limit, simplify or port the hot loop to C++.

---

## Parallel exploration: one orchestrator, three agents

This is the run shown in the session. It needs an agentic tool that can start
sub-agents and run commands (for example Claude Code). With a chat-only tool,
open three chats and paste one strategy into each.

```
Start 3 agents in parallel. Each one improves the bot in bots/voronoi_v2_bot.py
with a different strategy:
  A: look one move ahead for both players and pick the best worst case
  B: once the players are separated, fill the remaining space as well as possible
  C: cut the opponent off while keeping enough room for yourself
Rules for every agent:
  - create only its own file, bots/v3_<name>_bot.py; edit nothing else
  - standard library only; read all input every turn, flush, debug to stderr
  - keep every turn under 25 ms and report the worst turn measured
  - test with: python3 tournament.py bots/v3_<name>_bot.py bots/voronoi_v2_bot.py --games 60
  - at most 3 versions, about 12 minutes, then stop
  - report: the idea in 2 sentences, results, worst turn time, an honest verdict
When all three finish, run every new bot against voronoi_v2 and against each
other with 200 games on fresh seeds (--offset 5000) and give me one table.
```

What happened when we ran it: all three beat v2 (71%, 99%, 86%), and all
three reported that the gain came from the endgame rather than from the
strategy they were given. Head to head, the bot with the best score against
v2 (endgame, 99%) lost 44–56 to the aggressor. Pick by the whole pool.

---

## Rules of thumb for the whole team

- Submit v0 within the first hour. A safe bot that never crashes already scores.
- Re-submit only when gauntlet.py says the new version is better.
- Same seed, same bots, before/after: never compare runs with different settings.
- 40 games is not enough to tell 60% from 50%. Use 100 to 200.
- Keep every version. If a submission scores worse on the judge, roll back.
- Cite AI use in a comment at the top of the file (tool + date). The rules
  still require internet resources to be referenced in code comments.
