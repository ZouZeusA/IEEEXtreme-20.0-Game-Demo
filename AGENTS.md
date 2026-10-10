# Notes for AI coding agents (Devin, Claude Code, Cursor, Codex...)

This repo is a teaching kit for IEEEXtreme 20.0 game-type tasks: a 2-player
Tron-style game ("Light Cycles"), a local referee, a tournament runner and
bots of increasing strength. Python 3.8+ standard library only. No installs.

## Run

```bash
python3 referee.py "python3 bots/flood_bot.py" "python3 bots/safe_bot.py" --seed 3 --html replay.html
python3 tournament.py bots/voronoi_v2_bot.py bots/safe_bot.py --games 200 --offset 5000
python3 tournament.py bots/voronoi_v2_bot.py bots/safe_bot.py --games 200 --offset 5000 --html reports/v2_vs_safe.html
python3 gauntlet.py bots/voronoi_v2_bot.py --games 100 --offset 5000
make test        # smoke tests (python3 -m unittest discover -s tests -v)
./demo.sh        # the live-demo sequence, step by step
```

Always run from the repository root.

## Layout

- `referee.py`: plays one game. Starts two bot processes, talks to them over
  stdin/stdout, enforces 100 ms per turn (1 s on turn 1), applies simultaneous
  moves, decides the winner. `--html` writes a replay via `replay.py`.
- `tournament.py`: N games between two bots on seeds `offset .. offset+N-1`,
  swapping sides every game. Prints wins, score (win = 1, draw = 0.5) and how
  bot A died. `--html` writes a clickable report of every game.
- `gauntlet.py`: one bot against every other bot in `bots/`; prints the pool
  average and the worst opponent.
- `replay.py`: the HTML viewers (single game and tournament report).
- `tests/`: smoke tests; run them after any change.
- `bots/*.py`: one bot per file. Protocol is in README.md.

## Rules when you change or add a bot

1. Never edit `referee.py`, `tournament.py` or another bot to make a bot look better.
2. A new bot is a new file: `bots/v<N>_<name>_bot.py`. Keep old versions.
3. Read all input every turn, print exactly one move, flush, debug only to stderr.
4. Keep the worst turn under 25 ms on the 15x10 board and report it.
5. Claim an improvement only with numbers: at least 200 games with
   `--offset 5000` (boards the bot was not tuned on) against `voronoi_v2_bot.py`
   and against `safe_bot.py`, plus `gauntlet.py`. Report the table, including
   how the bot died and the worst opponent.
6. One change per version, so the effect of each change is measurable.
