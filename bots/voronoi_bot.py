#!/usr/bin/env python3
"""
Level 3: Voronoi territory. For each safe move, run two BFS (from my new head
and from the opponent's head) and count the cells I reach strictly first minus
the cells they reach first. Grab territory instead of just surviving.
If we are already walled off from each other, fall back to plain flood fill.

This is the kind of bot an AI assistant can draft fast, but you only KNOW it is
better after the local tournament says so.
"""
import sys
from collections import deque

DIRS = {"UP": (0, -1), "DOWN": (0, 1), "LEFT": (-1, 0), "RIGHT": (1, 0)}
INF = 10 ** 9


def bfs(grid, w, h, sx, sy):
    dist = [[INF] * w for _ in range(h)]
    dist[sy][sx] = 0
    q = deque([(sx, sy)])
    while q:
        x, y = q.popleft()
        for dx, dy in DIRS.values():
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h and grid[ny][nx] == "." and dist[ny][nx] == INF:
                dist[ny][nx] = dist[y][x] + 1
                q.append((nx, ny))
    return dist


def evaluate(grid, w, h, me_xy, opp_xy):
    d_me = bfs(grid, w, h, *me_xy)
    d_op = bfs(grid, w, h, *opp_xy)
    mine = theirs = 0
    touching = False
    for y in range(h):
        for x in range(w):
            a, b = d_me[y][x], d_op[y][x]
            if a < INF and b < INF:
                touching = True
            if a < b:
                mine += 1
            elif b < a:
                theirs += 1
    if not touching:  # separated: whoever has more room wins, so maximize room
        return 1000 + mine
    return mine - theirs


def main():
    w, h, me = map(int, sys.stdin.readline().split())
    while True:
        line = sys.stdin.readline()
        if not line:
            return
        heads = [tuple(map(int, line.split())), tuple(map(int, sys.stdin.readline().split()))]
        grid = [list(sys.stdin.readline().strip()) for _ in range(h)]
        (x, y), opp = heads[me], heads[1 - me]
        best, best_score = "UP", -INF
        for d, (dx, dy) in DIRS.items():
            nx, ny = x + dx, y + dy
            if not (0 <= nx < w and 0 <= ny < h and grid[ny][nx] == "."):
                continue
            grid[ny][nx] = "#"  # pretend we moved there
            score = evaluate(grid, w, h, (nx, ny), opp)
            # the opponent's BFS starts from a blocked cell; that is fine, BFS only
            # checks neighbours. Penalise cells the opponent could also enter now
            # (head-on collision = draw at best).
            if abs(nx - opp[0]) + abs(ny - opp[1]) == 1:
                score -= 5
            grid[ny][nx] = "."
            if score > best_score:
                best, best_score = d, score
        print(best, flush=True)


main()
