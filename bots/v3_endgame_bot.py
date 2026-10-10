#!/usr/bin/env python3
"""
Level 5 (v3): voronoi_v2 while in contact + a space-filling endgame.

Contact phase: voronoi_v2 (dead-end filter, then Voronoi), except that a move
which separates the players is scored by comparing both sides' fill estimates
(v2 took any separation, even into the smaller region).
Separated phase (no free cell reachable by both players): the winner is
whoever survives longer, so we maximise the length of the path we can
actually walk, not the raw cell count:
  - time-boxed iterative-deepening DFS over our own moves,
  - leaf value = best single pocket reachable from the head (pockets split
    by our own trail are counted separately, we can only enter one), with a
    checkerboard-parity bound (a path alternates colours),
  - tie-break inside the search: hug walls and trails (sum of blocked
    neighbours along the path), so we waste fewer cells.
"""
import sys
import time
from collections import deque

DIRS = {"UP": (0, -1), "DOWN": (0, 1), "LEFT": (-1, 0), "RIGHT": (1, 0)}
INF = 10 ** 9
BUDGET = 0.008  # seconds for the endgame search; keeps worst turn well under 25 ms


# ---------------- contact phase: voronoi_v2, unchanged ----------------
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


def evaluate(grid, w, h, me_xy, opp_xy, filler=None):
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
    if not touching:
        if filler is None:
            return 1000 + mine
        # separation: decided by who can walk the longer path from here
        free = bytearray(1 if grid[i // w][i % w] == "." else 0 for i in range(w * h))
        mine_len = filler.pockets_value(free, me_xy[1] * w + me_xy[0])
        opp_len = filler.pockets_value(free, opp_xy[1] * w + opp_xy[0]) - 1
        diff = mine_len - opp_len
        if diff > 0:
            return 1000 + diff
        if diff < 0:
            return -1000 + diff
        return -50  # likely draw
    return mine - theirs


def voronoi_move(grid, w, h, x, y, opp, filler=None):
    room = {}
    for d, (dx, dy) in DIRS.items():
        nx, ny = x + dx, y + dy
        if 0 <= nx < w and 0 <= ny < h and grid[ny][nx] == ".":
            grid[ny][nx] = "#"
            dist = bfs(grid, w, h, nx, ny)
            room[d] = sum(1 for row in dist for v in row if v < INF)
            grid[ny][nx] = "."
    if not room:
        return "UP"
    biggest = max(room.values())
    candidates = [d for d, r in room.items() if r >= 0.6 * biggest]
    best, best_score = candidates[0], -INF
    for d in candidates:
        dx, dy = DIRS[d]
        nx, ny = x + dx, y + dy
        grid[ny][nx] = "#"
        score = evaluate(grid, w, h, (nx, ny), opp, filler)
        if abs(nx - opp[0]) + abs(ny - opp[1]) == 1:
            score -= 5
        grid[ny][nx] = "."
        if score > best_score:
            best, best_score = d, score
    return best


# ---------------- separated phase: space filling ----------------
class Timeout(Exception):
    pass


class Filler:
    def __init__(self, w, h):
        self.w, self.h = w, h
        n = w * h
        self.color = [((i % w) + (i // w)) & 1 for i in range(n)]
        self.nbrs = []
        for i in range(n):
            x, y = i % w, i // w
            lst = []
            for dx, dy in DIRS.values():
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h:
                    lst.append(ny * w + nx)
            self.nbrs.append(lst)
        self.mark = [0] * n
        self.stamp = 0

    def pockets_value(self, free, head):
        """Best parity-bounded path length over the pockets touching head."""
        nbrs, color, mark = self.nbrs, self.color, self.mark
        self.stamp += 1
        st = self.stamp
        hc = color[head]
        best = 0
        for s in nbrs[head]:
            if not free[s] or mark[s] == st:
                continue
            mark[s] = st
            stack = [s]
            same = other = 0  # same colour as head / other colour
            while stack:
                c = stack.pop()
                if color[c] == hc:
                    same += 1
                else:
                    other += 1
                for nb in nbrs[c]:
                    if free[nb] and mark[nb] != st:
                        mark[nb] = st
                        stack.append(nb)
            # path from head: other, same, other, ...
            v = 2 * min(same, other) + (1 if other > same else 0)
            if v > best:
                best = v
        return best

    def blocked(self, free, c):
        nb = self.nbrs[c]
        return 4 - len(nb) + sum(1 for n in nb if not free[n])

    def ordered(self, free, head):
        moves = [n for n in self.nbrs[head] if free[n]]
        moves.sort(key=lambda n: -self.blocked(free, n))
        return moves

    def search(self, free, head, depth):
        """Value = 1000 * path length (parity bound at leaves) + wall-hug sum."""
        if time.perf_counter() > self.deadline:
            raise Timeout
        if depth == 0:
            return 1000 * self.pockets_value(free, head)
        best = 0
        for n in self.ordered(free, head):
            hug = self.blocked(free, n)
            free[n] = 0
            v = 1000 + hug + self.search(free, n, depth - 1)
            free[n] = 1
            if v > best:
                best = v
        return best

    def choose(self, free, head):
        """Return the neighbour cell index to move to (or None)."""
        moves = self.ordered(free, head)
        if not moves:
            return None
        if len(moves) == 1:
            return moves[0]
        self.deadline = time.perf_counter() + BUDGET
        cap = self.pockets_value(free, head)  # upper bound on any path
        best_move = moves[0]
        depth = 1
        while depth <= cap:
            scores = []
            try:
                for n in moves:
                    hug = self.blocked(free, n)
                    free[n] = 0
                    try:
                        v = 1000 + hug + self.search(free, n, depth - 1)
                    finally:
                        free[n] = 1
                    scores.append((v, n))
            except Timeout:
                break
            scores.sort(key=lambda t: -t[0])
            best_move = scores[0][1]
            moves = [t[1] for t in scores]  # best first next iteration
            depth += 1
        return best_move


def touching(grid, w, h, me, opp):
    """True if some free cell is reachable by both players."""
    seen = [[False] * w for _ in range(h)]
    q = deque()
    for dx, dy in DIRS.values():
        nx, ny = me[0] + dx, me[1] + dy
        if 0 <= nx < w and 0 <= ny < h and grid[ny][nx] == "." and not seen[ny][nx]:
            seen[ny][nx] = True
            q.append((nx, ny))
    while q:
        x, y = q.popleft()
        if abs(x - opp[0]) + abs(y - opp[1]) == 1:
            return True
        for dx, dy in DIRS.values():
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h and grid[ny][nx] == "." and not seen[ny][nx]:
                seen[ny][nx] = True
                q.append((nx, ny))
    return False


def main():
    w, h, me = map(int, sys.stdin.readline().split())
    filler = Filler(w, h)
    while True:
        line = sys.stdin.readline()
        if not line:
            return
        heads = [tuple(map(int, line.split())), tuple(map(int, sys.stdin.readline().split()))]
        grid = [list(sys.stdin.readline().strip()) for _ in range(h)]
        (x, y), opp = heads[me], heads[1 - me]
        if touching(grid, w, h, (x, y), opp):
            move = voronoi_move(grid, w, h, x, y, opp, filler)
        else:
            free = bytearray(1 if grid[i // w][i % w] == "." else 0 for i in range(w * h))
            tgt = filler.choose(free, y * w + x)
            move = "UP"
            if tgt is not None:
                tx, ty = tgt % w, tgt // w
                for d, (dx, dy) in DIRS.items():
                    if (x + dx, y + dy) == (tx, ty):
                        move = d
                        break
        sys.stdout.write(move + "\n")
        sys.stdout.flush()


if __name__ == "__main__":
    try:
        main()
    except (BrokenPipeError, KeyboardInterrupt):
        pass
