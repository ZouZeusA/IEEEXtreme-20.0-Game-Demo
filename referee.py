#!/usr/bin/env python3
"""
Local referee for a CodinGame-style 2-player game ("Light Cycles", a Tron clone).

Why this exists: in IEEEXtreme 20.0 game-type tasks, your program talks to bots
through stdin/stdout. The judge's bots are hidden, so the ONLY fast feedback loop
you have is a local referee + local opponents. Build this first, then the bot.

PROTOCOL (what each bot sees)
  Init (once):   W H my_id                  e.g. "15 10 0"
  Every turn:    x0 y0                       head of player 0
                 x1 y1                       head of player 1
                 H lines of W chars          '.' free, '#' wall or trail
  Bot replies:   UP | DOWN | LEFT | RIGHT    one line, then FLUSH

RULES
  Both players move simultaneously. You die if you leave the grid, enter a
  non-free cell, both heads enter the same cell (both die), print an invalid
  move, or exceed the time limit. Last cycle alive wins; both dead = draw.

Usage:
  python3 referee.py "python3 bots/flood_bot.py" "python3 bots/safe_bot.py" --seed 7 --show
"""
import argparse
import queue
import random
import shlex
import subprocess
import sys
import threading
import time

DIRS = {"UP": (0, -1), "DOWN": (0, 1), "LEFT": (-1, 0), "RIGHT": (1, 0)}


class Bot:
    """Wraps a bot process. A reader thread lets us enforce per-turn time limits."""

    def __init__(self, cmd):
        self.proc = subprocess.Popen(
            shlex.split(cmd),
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,  # bots may print debug info to stderr
            text=True,
            bufsize=1,
        )
        self.lines = queue.Queue()
        threading.Thread(target=self._pump, daemon=True).start()

    def _pump(self):
        for line in self.proc.stdout:
            self.lines.put(line.strip())
        self.lines.put(None)  # EOF

    def send(self, text):
        try:
            self.proc.stdin.write(text + "\n")
            self.proc.stdin.flush()
        except (BrokenPipeError, OSError):
            pass

    def read(self, timeout):
        try:
            return self.lines.get(timeout=timeout)
        except queue.Empty:
            return "TIMEOUT"

    def kill(self):
        try:
            self.proc.stdin.close()
        except Exception:
            pass
        try:
            self.proc.kill()
        except Exception:
            pass


def make_grid(w, h, rng, n_walls):
    """Point-symmetric random walls so neither side has an advantage."""
    grid = [["." for _ in range(w)] for _ in range(h)]
    for _ in range(n_walls):
        x, y = rng.randrange(w), rng.randrange(h)
        grid[y][x] = "#"
        grid[h - 1 - y][w - 1 - x] = "#"
    return grid


def play(cmd0, cmd1, w=15, h=10, seed=0, n_walls=6, turn_ms=100, first_ms=1000, show=False):
    rng = random.Random(seed)
    grid = make_grid(w, h, rng, n_walls)
    sy = rng.randrange(1, h - 1)
    pos = [(2, sy), (w - 3, h - 1 - sy)]
    walls = [(x, y) for y in range(h) for x in range(w) if grid[y][x] == "#"]
    start = [list(p) for p in pos]
    for x, y in pos:
        grid[y][x] = "#"
    frames = []  # one entry per turn, for the HTML replay

    bots = [Bot(cmd0), Bot(cmd1)]
    for i, b in enumerate(bots):
        b.send(f"{w} {h} {i}")

    alive = [True, True]
    reason = ["", ""]
    turn = 0
    try:
        while all(alive) and turn < w * h:
            state = "\n".join(
                [f"{pos[0][0]} {pos[0][1]}", f"{pos[1][0]} {pos[1][1]}"]
                + ["".join(r) for r in grid]
            )
            limit = (first_ms if turn == 0 else turn_ms) / 1000.0
            moves = [None, None]
            for i, b in enumerate(bots):
                b.send(state)
            for i, b in enumerate(bots):
                t0 = time.perf_counter()
                ans = bots[i].read(limit)
                if ans == "TIMEOUT" or (time.perf_counter() - t0) > limit:
                    alive[i], reason[i] = False, "timeout"
                elif ans not in DIRS:
                    alive[i], reason[i] = False, f"invalid output {ans!r}"
                else:
                    moves[i] = ans

            new = list(pos)
            for i in range(2):
                if not alive[i]:
                    continue
                dx, dy = DIRS[moves[i]]
                nx, ny = pos[i][0] + dx, pos[i][1] + dy
                if not (0 <= nx < w and 0 <= ny < h):
                    alive[i], reason[i] = False, "left the grid"
                elif grid[ny][nx] != ".":
                    alive[i], reason[i] = False, "crashed into a trail"
                new[i] = (nx, ny)
            if alive[0] and alive[1] and new[0] == new[1]:
                alive = [False, False]
                reason = ["head-on collision", "head-on collision"]
            crash = [None, None]
            for i in range(2):
                if alive[i]:
                    pos[i] = new[i]
                    grid[new[i][1]][new[i][0]] = "#"
                elif moves[i] is not None and new[i] != pos[i]:
                    crash[i] = new[i]
            turn += 1
            frames.append({"m": moves, "p": [list(pos[0]), list(pos[1])],
                           "a": list(alive), "x": crash})

            if show:
                frame = [r[:] for r in grid]
                for i, c in enumerate("AB"):
                    frame[pos[i][1]][pos[i][0]] = c
                print(f"\n--- turn {turn}  moves: {moves}")
                print("\n".join("".join(r) for r in frame))
    finally:
        for b in bots:
            b.kill()

    if alive[0] and not alive[1]:
        result = 0
    elif alive[1] and not alive[0]:
        result = 1
    else:
        result = -1  # draw
    replay = {"w": w, "h": h, "seed": seed, "walls": walls, "start": start,
              "frames": frames, "result": result, "reason": reason}
    return {"result": result, "turns": turn, "reason": reason, "replay": replay}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("bot0")
    ap.add_argument("bot1")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--show", action="store_true", help="print the board every turn")
    args = ap.parse_args()
    r = play(args.bot0, args.bot1, seed=args.seed, show=args.show)
    who = {0: "bot0 (A) wins", 1: "bot1 (B) wins", -1: "draw"}[r["result"]]
    print(f"\n{who} after {r['turns']} turns. Death reasons: {r['reason']}")


if __name__ == "__main__":
    sys.exit(main())
