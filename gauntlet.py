#!/usr/bin/env python3
"""
Play one bot against EVERY other bot in bots/ and print a table.

Why: the judge's bots are hidden and may play differently from yours.
A change that beats your last version can lose to a dumber bot (we saw
exactly that: voronoi v1 beat flood but lost more often to safe than
flood did). Always test against a pool, not just against yourself.

How it works: for every other file in bots/, it runs tournament.py
(your bot = A, that file = B) and collects A's score. The pool average says how
good your bot is in general; the worst opponent says where it is weakest.

Usage:
  python3 gauntlet.py bots/voronoi_v2_bot.py --games 100 --offset 5000
"""
import argparse
import glob
import math
import os
import subprocess
import sys


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("bot")
    ap.add_argument("--games", type=int, default=100)
    ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--offset", type=int, default=0)
    args = ap.parse_args()

    here = os.path.dirname(os.path.abspath(__file__))
    pool = sorted(p for p in glob.glob(os.path.join(here, "bots", "*.py"))
                  if os.path.abspath(p) != os.path.abspath(args.bot))
    print(f"{'opponent':<22} {'score':>6}  {'+/- 2 SE':>8}")
    scores = []
    for opp in pool:
        out = subprocess.run(
            [sys.executable, os.path.join(here, "tournament.py"), args.bot, opp,
             "--games", str(args.games), "--workers", str(args.workers),
             "--offset", str(args.offset)],
            capture_output=True, text=True, cwd=here,
        ).stdout
        line = next(l for l in out.splitlines() if l.startswith("A score"))
        p = float(line.split(":")[1].strip().rstrip("%")) / 100
        se = math.sqrt(p * (1 - p) / args.games)
        print(f"{os.path.basename(opp):<22} {p:>6.0%}  {2 * se:>8.0%}")
        scores.append(p)
    if scores:
        print(f"{'pool average':<22} {sum(scores) / len(scores):>6.0%}")
        print(f"{'worst opponent':<22} {min(scores):>6.0%}")


if __name__ == "__main__":
    main()
