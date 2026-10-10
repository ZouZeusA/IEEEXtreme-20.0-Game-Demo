#!/usr/bin/env python3
"""
v3 aggressor: simultaneous-move 2-ply Voronoi that tries to cut the opponent off.

For each of my safe moves (after a dead-end filter) we look at every opponent
reply, block both cells, and score the Voronoi split with the opponent's
territory weighted MORE than ours (we gain by shrinking them, not only by
growing). We take the worst case over the opponent's replies, so a cell the
opponent can also enter scores as a draw (0): we only accept that gamble when
every other move is losing on territory. Once the board is
split we switch to survival: longest path search with a node budget.
"""
import sys
import time

DIRS = (("UP", 0, -1), ("DOWN", 0, 1), ("LEFT", -1, 0), ("RIGHT", 1, 0))
AGGR = 1.3        # weight on opponent territory (see note below)
PULL = 0.0        # pull toward opponent; 0.5 per step measured 67% vs v2 (88% without)
# Note: start squares have odd distance, so Voronoi never ties and mine + theirs
# is the whole shared area; AGGR therefore rarely changes the ranking. The win
# over v2 comes from the 2-ply worst-case reply and the longest-path endgame.
SPLIT_BONUS = 200


def build_nbrs(w, h):
    nb = []
    for y in range(h):
        for x in range(w):
            l = []
            if y > 0: l.append((y - 1) * w + x)
            if y < h - 1: l.append((y + 1) * w + x)
            if x > 0: l.append(y * w + x - 1)
            if x < w - 1: l.append(y * w + x + 1)
            nb.append(l)
    return nb


def bfs(free, nbrs, start, n):
    dist = [-1] * n
    dist[start] = 0
    frontier = [start]
    d = 0
    while frontier:
        d += 1
        nxt = []
        for c in frontier:
            for b in nbrs[c]:
                if free[b] and dist[b] < 0:
                    dist[b] = d
                    nxt.append(b)
        frontier = nxt
    return dist


def room(free, nbrs, start, n):
    seen = [False] * n
    seen[start] = True
    stack = [start]
    cnt = 0
    while stack:
        c = stack.pop()
        for b in nbrs[c]:
            if free[b] and not seen[b]:
                seen[b] = True
                cnt += 1
                stack.append(b)
    return cnt


def voronoi(free, nbrs, p, q, n):
    dm = bfs(free, nbrs, p, n)
    do = bfs(free, nbrs, q, n)
    mine = theirs = 0
    touching = False
    for c in range(n):
        if not free[c]:
            continue
        a, b = dm[c], do[c]
        if a >= 0:
            if b >= 0:
                touching = True
                if a < b:
                    mine += 1
                elif b < a:
                    theirs += 1
            else:
                mine += 1
        elif b >= 0:
            theirs += 1
    return mine, theirs, touching, dm[q] if dm[q] >= 0 else None


def longest(free, nbrs, start, budget):
    """Depth-first longest path from start (start already blocked), node budget."""
    best = 0
    count = 0
    stack = [[start, 0]]
    while stack:
        fr = stack[-1]
        c = fr[0]
        nb = nbrs[c]
        i = fr[1]
        k = len(nb)
        while i < k and not free[nb[i]]:
            i += 1
        if i < k and count < budget:
            fr[1] = i + 1
            b = nb[i]
            free[b] = False
            count += 1
            stack.append([b, 0])
            if len(stack) - 1 > best:
                best = len(stack) - 1
        else:
            stack.pop()
            if stack:
                free[c] = True
    return best


def decide(w, h, me, heads, rows):
    n = w * h
    nbrs = decide.nbrs
    if nbrs is None or len(nbrs) != n:
        nbrs = decide.nbrs = build_nbrs(w, h)
    free = [ch == "." for r in rows for ch in r[:w]]
    (x, y), (ox, oy) = heads[me], heads[1 - me]
    p, q = y * w + x, oy * w + ox
    free[p] = free[q] = False

    moves = []
    for name, dx, dy in DIRS:
        nx, ny = x + dx, y + dy
        if 0 <= nx < w and 0 <= ny < h and free[ny * w + nx]:
            moves.append((name, ny * w + nx))
    if not moves:
        return "UP"
    if len(moves) == 1:
        return moves[0][0]

    opp_moves = [b for b in nbrs[q] if free[b]]

    # dead-end filter
    rooms = {}
    for name, c in moves:
        free[c] = False
        rooms[name] = room(free, nbrs, c, n)
        free[c] = True
    biggest = max(rooms.values())
    cands = [(nm, c) for nm, c in moves if rooms[nm] >= 0.6 * biggest]

    # are we already separated?
    dm = bfs(free, nbrs, p, n)
    connected = any(dm[b] >= 0 for b in nbrs[q])
    if not connected:
        best, bv = None, -1
        budget = 2400 // len(cands)
        for nm, c in cands:
            free[c] = False
            v = longest(free, nbrs, c, budget) * 1000 + rooms[nm] * 10 \
                - sum(1 for b in nbrs[c] if free[b])
            free[c] = True
            if v > bv:
                best, bv = nm, v
        return best

    dist_to_opp = dm[q] if dm[q] >= 0 else min(
        (dm[b] for b in nbrs[q] if dm[b] >= 0), default=0) + 1
    half = (sum(free) - 2) / 2.0
    best, bv = cands[0][0], -1e18
    for nm, c in cands:
        free[c] = False
        worst = 1e18
        total = 0.0
        for o in (opp_moves or [None]):
            if o is None:
                val = 10000.0           # opponent has no move: it dies
            elif o == c:
                val = 0.0               # head-on: draw
            else:
                free[o] = False
                mine, theirs, touching, dmq = voronoi(free, nbrs, c, o, n)
                free[o] = True
                if not touching:
                    diff = mine - theirs
                    val = (SPLIT_BONUS if diff > 0 else -SPLIT_BONUS if diff < 0 else 0) + diff
                else:
                    val = mine - AGGR * theirs + (AGGR - 1) * half
                    if dmq is not None:
                        val -= PULL * dmq
            if val < worst:
                worst = val
            total += val
        free[c] = True
        score = 0.8 * worst + 0.2 * total / max(1, len(opp_moves))
        if score > bv:
            best, bv = nm, score
    return best


decide.nbrs = None


def main():
    first = sys.stdin.readline()
    if not first:
        return
    w, h, me = map(int, first.split())
    while True:
        line = sys.stdin.readline()
        if not line:
            return
        l2 = sys.stdin.readline()
        heads = [tuple(map(int, line.split())), tuple(map(int, l2.split()))]
        rows = [sys.stdin.readline().strip() for _ in range(h)]
        try:
            mv = decide(w, h, me, heads, rows)
        except Exception:
            mv = "UP"
        sys.stdout.write(mv + "\n")
        sys.stdout.flush()


if __name__ == "__main__":
    main()
