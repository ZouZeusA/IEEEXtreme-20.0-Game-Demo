#!/usr/bin/env python3
"""
Level 2: for each safe move, BFS (flood fill) from the new cell and count how
much free space is still reachable. Pick the move that keeps the most room.
This is the same BFS template from the graph session, reused as a heuristic.
"""
import sys
from collections import deque

DIRS = {"UP": (0, -1), "DOWN": (0, 1), "LEFT": (-1, 0), "RIGHT": (1, 0)}


def reachable(grid, w, h, sx, sy):
    seen = {(sx, sy)}
    q = deque([(sx, sy)])
    while q:
        x, y = q.popleft()
        for dx, dy in DIRS.values():
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h and grid[ny][nx] == "." and (nx, ny) not in seen:
                seen.add((nx, ny))
                q.append((nx, ny))
    return len(seen)


def main():
    w, h, me = map(int, sys.stdin.readline().split())
    while True:
        line = sys.stdin.readline()
        if not line:
            return
        heads = [tuple(map(int, line.split())), tuple(map(int, sys.stdin.readline().split()))]
        grid = [sys.stdin.readline().strip() for _ in range(h)]
        x, y = heads[me]
        best, best_score = "UP", -1
        for d, (dx, dy) in DIRS.items():
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h and grid[ny][nx] == ".":
                score = reachable(grid, w, h, nx, ny)
                if score > best_score:
                    best, best_score = d, score
        print(best, flush=True)


main()
