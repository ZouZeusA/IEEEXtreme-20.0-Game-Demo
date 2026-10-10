# IEEEXtreme-20.0-Game-Demo

Two "light cycles" move on a 15×10 grid with some fixed walls, both at the
same time each turn. Each one leaves a trail that becomes a wall. A bot dies if
it leaves the grid, hits a wall or trail, takes longer than 100 ms, or prints
something invalid. If both enter the same cell, both die. Last one alive wins.

This repo is a teaching kit for the **game-type tasks of IEEEXtreme 20.0**,
where your program plays against bots turn by turn through standard input and
output, and AI use is allowed. It contains a local referee, a CodinGame-style
replay viewer, a tournament runner with clickable per-game reports, a gauntlet,
and bots of increasing strength, three of them written by AI agents in
parallel. It was built for the session "AI for IEEEXtreme 20.0" (IEEEXtreme
Global Masterclass 3.0, 10 October 2026).

Python 3.8+ standard library only. Nothing to install.

## Quick start

```bash
git clone https://github.com/ZouZeusA/IEEEXtreme-20.0-Game-Demo.git
cd IEEEXtreme-20.0-Game-Demo

# optional: an isolated environment (there are no dependencies to install)
python3 -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate

make test        # or: python3 -m unittest discover -s tests -v
./demo.sh        # the live demo, one step per Enter; each step opens its own report
```

On macOS the reports open in Google Chrome if it is installed, otherwise in
your default browser. `WORKERS=8 ./demo.sh` uses more CPU cores;
`NO_OPEN=1 ./demo.sh` opens nothing and just prints the report paths.

## How the pieces fit

```
bots/*.py ──stdin/stdout──► referee.py ──► one game        (--html: watch it)
                               ▲
tournament.py ── runs it N times, one board per seed ──► win rate + how A died
                                                    (--html: click any game)
gauntlet.py ── runs a tournament against EVERY bot in bots/ ──► pool average
demo.sh ── runs all of the above in the order of the talk
```

| File | What it does |
|---|---|
| `referee.py` | Plays one game. Starts both bots as separate programs, sends the board every turn, reads one move from each, enforces 100 ms per turn (1 s on turn 1), applies both moves at once, decides the winner. `--html` writes a replay. |
| `replay.py` | Builds the HTML pages: the single-game replay and the tournament report. |
| `tournament.py` | Plays N games between bot A and bot B. Seed = board, so one seed works like one test case. Sides swap every game. Prints A's score (win = 1, draw = 0.5) and how A died. `--offset 5000` uses boards you never tuned on. `--html` writes a report: one tile per game, filters for A won / A lost / draws / cause of death, click any tile to watch that game. |
| `gauntlet.py` | Runs a tournament between your bot and every other bot in `bots/`. Prints one row per opponent, the pool average and the worst opponent. |
| `demo.sh` | The live demo, step by step. |
| `tests/test_smoke.py` | Every bot plays legal moves in time, the viewers render, v2 beats random. |
| `templates/` | Game-loop skeletons in Python and C++. |
| `PROMPTS.md` | Prompts for the multi-agent workflow, including the 3-agent run. |
| `LEARNING_PROMPTS.md` | Coach prompts for practising locked-workspace tasks with AI. |
| `AGENTS.md` | Rules for AI coding agents working in this repo. |

## The bots

Every bot is a separate program that reads the board and prints a move. In a
match, one bot is "yours" (A) and the other is the opponent (B); any bot can
play either role.

| Bot | Idea |
|---|---|
| `random_bot` | Random direction. Proves the input/output loop works. |
| `safe_bot` | Random among the moves that don't crash right away. |
| `flood_bot` | For each move, BFS from the new cell and count the free cells still reachable. Keep the most room. |
| `voronoi_bot` | BFS from both heads; count the cells it reaches first minus the cells the opponent reaches first. Grab territory. |
| `voronoi_v2_bot` | Drop moves that leave much less room than the best move (dead-end filter), then play like voronoi. |
| `v3_lookahead_bot` | Written by AI agent A. Tries all 4×4 pairs of (my move, opponent move) and picks the best worst case. |
| `v3_endgame_bot` | Written by AI agent B. Once the players are walled apart, a time-boxed search for the longest path it can actually walk. |
| `v3_aggressor_bot` | Written by AI agent C. Checks every opponent reply, plus a longest-path endgame. |

The idea behind the kit: on contest day the judge's opponents are hidden. The
bots in `bots/` are stand-ins for them. Your next version has to beat the whole
pool, including your own previous versions, before you submit it.

## Results measured on this kit

200 games per pairing, sides swapped. "Fresh" = seeds 5000–5199, which none of
the bots were tuned on. Numbers move a few points between runs and machines
(`safe_bot` and `random_bot` are random; `v3_endgame_bot` searches for a fixed
time, so it plays better on a faster CPU).

| Bot A | Bot B | A score | Seeds |
|---|---|---|---|
| random | safe | 2% | fresh |
| flood | safe | 88–93% | fresh |
| voronoi v1 | safe | 72–78% | fresh |
| voronoi v1 | flood | 60% | 0–199 |
| voronoi v2 | safe | 98–100% | fresh |
| v3 lookahead | voronoi v2 | 71% | fresh |
| v3 endgame | voronoi v2 | 99% | fresh |
| v3 aggressor | voronoi v2 | 86% | fresh |
| v3 aggressor | v3 endgame | 52–57% | fresh |

Gauntlet, 100 games per opponent on fresh boards:

| Bot | Pool average | Worst opponent |
|---|---|---|
| voronoi v2 | 57% | v3 endgame, 1% |
| v3 aggressor | 88% | v3 endgame, 54% |

## Protocol

```
Init:        W H my_id
Each turn:   x0 y0             head of player 0
             x1 y1             head of player 1
             H lines of W chars ('.' free, '#' wall or trail)
Reply:       UP | DOWN | LEFT | RIGHT   then flush
```

Bugs that kill most first bots, in any language:

1. Not flushing stdout. The referee waits, your bot waits, timeout.
2. Not reading the whole turn's input. Next turn you read stale lines and desync.
3. Printing debug text to stdout. Use stderr for debug.
4. Slow turns. Time each turn and answer by half the limit.

## Write your own bot

Copy `templates/game_loop_template.py` (or the C++ one) into `bots/`, change
`decide()`, then:

```bash
python3 tournament.py bots/my_bot.py bots/voronoi_v2_bot.py --games 200 --offset 5000 --html reports/mine.html
python3 gauntlet.py bots/my_bot.py --games 100 --offset 5000
```

A compiled bot works too: pass its executable path instead of a `.py` file.
