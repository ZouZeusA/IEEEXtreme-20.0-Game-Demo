#!/usr/bin/env python3
"""Level 1: random, but never steps into a wall or off the grid."""
import random
import sys

DIRS = {"UP": (0, -1), "DOWN": (0, 1), "LEFT": (-1, 0), "RIGHT": (1, 0)}


def main():
    w, h, me = map(int, sys.stdin.readline().split())
    while True:
        line = sys.stdin.readline()
        if not line:
            return
        heads = [tuple(map(int, line.split())), tuple(map(int, sys.stdin.readline().split()))]
        grid = [sys.stdin.readline().strip() for _ in range(h)]
        x, y = heads[me]
        safe = [d for d, (dx, dy) in DIRS.items()
                if 0 <= x + dx < w and 0 <= y + dy < h and grid[y + dy][x + dx] == "."]
        print(random.choice(safe) if safe else "UP", flush=True)


main()
