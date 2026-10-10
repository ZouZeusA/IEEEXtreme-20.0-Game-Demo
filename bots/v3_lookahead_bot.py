#!/usr/bin/env python3
"""
Level 5 (v3): one-turn simultaneous lookahead over Voronoi territory.

For every (my move, opponent move) pair of the next simultaneous turn, apply
both moves and score the position with a Voronoi evaluation (one combined
layered BFS). Head-on collision = draw (0), my crash = very negative, opponent
crash = very positive. Pick my move by maximin (best worst case), tie-broken by
the average. The v2 dead-end filter is kept: moves whose reachable room is far
below the best move's room are dropped first.
"""
import sys

DIRS = (("UP", 0, -1), ("DOWN", 0, 1), ("LEFT", -1, 0), ("RIGHT", 1, 0))
WIN, LOSS = 10000, -10000


def setup(w, h):
    nbr = []
    for i in range(w * h):
        x, y = i % w, i // w
        lst = []
        for _, dx, dy in DIRS:
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h:
                lst.append(ny * w + nx)
        nbr.append(lst)
    # move target per direction (or -1 if off-grid)
    step = []
    for i in range(w * h):
        x, y = i % w, i // w
        row = []
        for _, dx, dy in DIRS:
            nx, ny = x + dx, y + dy
            row.append(ny * w + nx if 0 <= nx < w and 0 <= ny < h else -1)
        step.append(row)
    return nbr, step


def room(free, nbr, s):
    """Cells reachable from s (s itself is treated as already occupied)."""
    seen = {s}
    stack = [s]
    while stack:
        c = stack.pop()
        for n in nbr[c]:
            if free[n] and n not in seen:
                seen.add(n)
                stack.append(n)
    return len(seen) - 1, seen


def fill_estimate(cells, head, color):
    """Upper bound on the path length a head can walk through `cells`:
    a path alternates checkerboard colours, starting on the colour opposite
    the head's."""
    hc = color[head]
    same = other = 0
    for c in cells:
        if c == head:
            continue
        if color[c] == hc:
            same += 1
        else:
            other += 1
    return 2 * min(same, other) + (1 if other > same else 0)


def voronoi(free, nbr, a, b, n_cells):
    """Layered simultaneous BFS from heads a (me) and b (opp).
    Returns (mine, theirs, touching)."""
    owner = [0] * n_cells  # 0 free/unseen, 1 me, 2 opp, 3 neutral, 4 me-tentative
    owner[a] = 1
    owner[b] = 2
    fa, fb = [a], [b]
    mine = theirs = 0
    touching = False
    while fa or fb:
        na = []
        for c in fa:
            for n in nbr[c]:
                if free[n]:
                    o = owner[n]
                    if o == 0:
                        owner[n] = 4
                        na.append(n)
                    elif o == 2 or o == 3:
                        touching = True
        nb = []
        for c in fb:
            for n in nbr[c]:
                if free[n]:
                    o = owner[n]
                    if o == 0:
                        owner[n] = 2
                        nb.append(n)
                    elif o == 4:
                        owner[n] = 3
                        touching = True
                    elif o == 1 or o == 3:
                        touching = True
        fa = []
        for n in na:
            if owner[n] == 4:
                owner[n] = 1
                fa.append(n)
        mine += len(fa)
        theirs += len(nb)
        fb = nb
    return mine, theirs, touching, owner


def score_pos(free, nbr, a, b, n_cells, color):
    mine, theirs, touching, owner = voronoi(free, nbr, a, b, n_cells)
    diff = mine - theirs
    if touching:
        return diff
    ma = [i for i in range(n_cells) if owner[i] == 1]
    tb = [i for i in range(n_cells) if owner[i] == 2]
    diff = fill_estimate(ma, a, color) - fill_estimate(tb, b, color)
    # separated: the bigger room should win the fill race
    if diff > 0:
        return 300 + diff
    if diff < 0:
        return -300 + diff
    return 0


def choose(free, nbr, step, me, op, n_cells, color):
    my_moves = [(d, step[me][k]) for k, (d, _, _) in enumerate(DIRS)
                if step[me][k] >= 0 and free[step[me][k]]]
    if not my_moves:
        return "UP"
    op_moves = [step[op][k] for k in range(4) if step[op][k] >= 0 and free[step[op][k]]]
    if len(my_moves) == 1:
        return my_moves[0][0]

    # dead-end filter (as in v2): drop moves with much less room than the best
    rooms = {}
    sep = True
    for d, t in my_moves:
        free[t] = False
        r, seen = room(free, nbr, t)
        free[t] = True
        if any(o in seen for o in op_moves):
            sep = False
        rooms[d] = (fill_estimate(seen, t, color), r)
    biggest = max(v[1] for v in rooms.values())
    cands = [(d, t) for d, t in my_moves if rooms[d][1] >= 0.6 * biggest]

    if sep or not op_moves:
        # alone in my chamber (or opponent crashes): pure space filling.
        # most fillable cells first, then hug walls (fewest free neighbours)
        def fkey(dt):
            d, t = dt
            free[t] = False
            deg = sum(1 for n in nbr[t] if free[n])
            free[t] = True
            return (rooms[d][0], -deg)
        return max(my_moves, key=fkey)[0]

    best_d, best_key = cands[0][0], None
    for d, t in cands:
        free[t] = False
        worst, total = WIN * 10, 0
        for o in op_moves:
            if o == t:
                s = 0  # head-on: both die
            else:
                free[o] = False
                s = score_pos(free, nbr, t, o, n_cells, color)
                free[o] = True
            total += s
            if s < worst:
                worst = s
        free[t] = True
        key = (worst, total / len(op_moves), rooms[d][0])
        if best_key is None or key > best_key:
            best_d, best_key = d, key
    return best_d


def main():
    first = sys.stdin.readline()
    if not first:
        return
    w, h, my_id = map(int, first.split())
    n_cells = w * h
    nbr, step = setup(w, h)
    color = [((i % w) + (i // w)) & 1 for i in range(n_cells)]
    while True:
        l0 = sys.stdin.readline()
        if not l0:
            return
        l1 = sys.stdin.readline()
        rows = [sys.stdin.readline().strip() for _ in range(h)]
        heads = [tuple(map(int, l0.split())), tuple(map(int, l1.split()))]
        free = [ch == "." for r in rows for ch in r]
        if len(free) != n_cells:  # malformed input: pad defensively
            free = (free + [False] * n_cells)[:n_cells]
        mx, my = heads[my_id]
        ox, oy = heads[1 - my_id]
        move = choose(free, nbr, step, my * w + mx, oy * w + ox, n_cells, color)
        sys.stdout.write(move + "\n")
        sys.stdout.flush()


if __name__ == "__main__":
    main()
