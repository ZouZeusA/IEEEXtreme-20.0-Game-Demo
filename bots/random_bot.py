#!/usr/bin/env python3
"""Level 0: picks a random direction. Exists to prove the I/O loop works."""
import random
import sys

DIRS = ["UP", "DOWN", "LEFT", "RIGHT"]


def main():
    w, h, me = map(int, sys.stdin.readline().split())
    while True:
        line = sys.stdin.readline()
        if not line:  # referee closed the pipe: game over
            return
        for _ in range(1 + h):  # read the WHOLE turn input, even if unused
            sys.stdin.readline()
        print(random.choice(DIRS), flush=True)  # flush, or the referee never sees it


main()
