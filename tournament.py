#!/usr/bin/env python3
"""
Run many games between two bots, swapping sides, and report win rate.
A bot change is only "better" if this number goes up. Gut feeling and AI
confidence do not count.

Each seed builds a different board, so one seed works like one test case.

Usage:
  python3 tournament.py bots/voronoi_bot.py bots/flood_bot.py --games 40
  python3 tournament.py A.py B.py --games 200 --offset 5000   # fresh seeds you never tuned on
  python3 tournament.py A.py B.py --games 200 --html reports/a_vs_b.html   # watch every game
"""
import argparse
import os
import shlex
import sys
from concurrent.futures import ProcessPoolExecutor
from collections import Counter

from referee import play


def cmd(bot_path):
    """Run a .py bot with the same Python that runs this script; anything else as is."""
    p = os.path.abspath(bot_path)
    if p.endswith(".py"):
        return f"{shlex.quote(sys.executable)} {shlex.quote(p)}"
    return shlex.quote(p)  # a compiled bot, e.g. ./bots/my_bot


def name(bot_path):
    return os.path.splitext(os.path.basename(bot_path))[0]


def one(args):
    """Play one game. Bot A starts as player 0 on even seeds and as player 1 on odd seeds."""
    a, b, seed = args
    a_idx = seed % 2
    r = play(cmd(a), cmd(b), seed=seed) if a_idx == 0 else play(cmd(b), cmd(a), seed=seed)
    if r["result"] == -1:
        winner = "draw"
    else:
        winner = "A" if r["result"] == a_idx else "B"
    reasons = r["reason"] if a_idx == 0 else r["reason"][::-1]  # always [A's death, B's death]
    return {"seed": seed, "a_idx": a_idx, "winner": winner, "reasons": reasons,
            "turns": r["turns"], "replay": r["replay"]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("bot_a")
    ap.add_argument("bot_b")
    ap.add_argument("--games", type=int, default=40)
    ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--offset", type=int, default=0,
                    help="first seed; use a new range to test on boards you did not tune on")
    ap.add_argument("--html", metavar="FILE",
                    help="write a report where you can click any game and watch it")
    args = ap.parse_args()

    jobs = [(args.bot_a, args.bot_b, s) for s in range(args.offset, args.offset + args.games)]
    with ProcessPoolExecutor(max_workers=args.workers) as ex:
        games = list(ex.map(one, jobs))

    tally = Counter(g["winner"] for g in games)
    deaths_a = Counter(g["reasons"][0] for g in games if g["reasons"][0])
    n = args.games
    score = (tally["A"] + 0.5 * tally["draw"]) / n
    print(f"A = {args.bot_a}\nB = {args.bot_b}")
    print(f"A wins {tally['A']}, B wins {tally['B']}, draws {tally['draw']}  (n={n})")
    print(f"A score (win=1, draw=0.5): {score:.0%}")
    print(f"How A died: {dict(deaths_a) or 'never'}")

    if args.html:
        from replay import write_report
        sub = f"{n} games · seeds {args.offset}–{args.offset + n - 1} · sides swapped every game"
        write_report(args.html, games, name(args.bot_a), name(args.bot_b), sub)
        print(f"Report written to {args.html}: open it and click any game to watch it.")


if __name__ == "__main__":
    main()
