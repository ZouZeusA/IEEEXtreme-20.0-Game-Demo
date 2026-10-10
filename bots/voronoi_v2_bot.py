#!/usr/bin/env python3
"""
Level 4 (v2): Voronoi territory + dead-end filter.

The v1 tournament showed v1 dying by "crashed into a trail" far too often:
it grabs territory and walks into pockets. Fix: first drop any move whose
reachable area is much smaller than the best move's, then pick by Voronoi.

Measured on the local referee (200 games each, sides swapped):
  v1 vs safe 72%  ->  v2 vs safe 99%
  v1 vs flood 60% ->  v2 vs flood 98%
  v2 vs v1        ->  ~53% (statistically a coin flip)
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
        # dead-end filter: room left after each safe move
        room = {}
        for d, (dx, dy) in DIRS.items():
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h and grid[ny][nx] == ".":
                grid[ny][nx] = "#"
                dist = bfs(grid, w, h, nx, ny)
                room[d] = sum(1 for row in dist for v in row if v < INF)
                grid[ny][nx] = "."
        if not room:
            print("UP", flush=True)
            continue
        biggest = max(room.values())
        candidates = [d for d, r in room.items() if r >= 0.6 * biggest]

        best, best_score = candidates[0], -INF
        for d in candidates:
            dx, dy = DIRS[d]
            nx, ny = x + dx, y + dy
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
