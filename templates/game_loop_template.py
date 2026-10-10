#!/usr/bin/env python3
"""Game-loop skeleton for stdin/stdout bot tasks. Adapt the parsing to your task's SPEC."""
import sys
import time

DIRS = {"UP": (0, -1), "DOWN": (0, 1), "LEFT": (-1, 0), "RIGHT": (1, 0)}


def decide(w, h, me, heads, grid, deadline):
    x, y = heads[me]
    for d, (dx, dy) in DIRS.items():
        if time.perf_counter() > deadline:
            break  # always answer something before the limit
        nx, ny = x + dx, y + dy
        if 0 <= nx < w and 0 <= ny < h and grid[ny][nx] == ".":
            return d
    return "UP"


def main():
    w, h, me = map(int, sys.stdin.readline().split())
    while True:
        line = sys.stdin.readline()
        if not line:          # referee closed the pipe: game over
            return
        start = time.perf_counter()
        heads = [tuple(map(int, line.split())), tuple(map(int, sys.stdin.readline().split()))]
        grid = [sys.stdin.readline().strip() for _ in range(h)]   # read the WHOLE turn
        move = decide(w, h, me, heads, grid, deadline=start + 0.05)  # half of a 100 ms limit
        print(f"turn took {1000 * (time.perf_counter() - start):.1f} ms", file=sys.stderr)
        print(move, flush=True)  # flush every turn


main()
