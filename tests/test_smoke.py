"""Smoke tests: every bot plays legal games, the viewers render, the ladder holds.

Run:  python3 -m unittest discover -s tests -v
"""
import glob
import os
import shlex
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from referee import play  # noqa: E402
from replay import write_html, write_report  # noqa: E402
import tournament  # noqa: E402

BOTS = sorted(glob.glob(os.path.join(ROOT, "bots", "*.py")))
SAFE = os.path.join(ROOT, "bots", "safe_bot.py")


def cmd(path):
    return f"{shlex.quote(sys.executable)} {shlex.quote(path)}"


class SmokeTests(unittest.TestCase):
    def test_every_bot_plays_legal_moves_in_time(self):
        for bot in BOTS:
            for seed in (1, 2):
                with self.subTest(bot=os.path.basename(bot), seed=seed):
                    r = play(cmd(bot), cmd(SAFE), seed=seed)
                    self.assertNotIn("timeout", r["reason"][0])
                    self.assertNotIn("invalid", r["reason"][0])
                    self.assertGreater(r["turns"], 0)

    def test_v2_beats_random(self):
        v2 = os.path.join(ROOT, "bots", "voronoi_v2_bot.py")
        rnd = os.path.join(ROOT, "bots", "random_bot.py")
        games = [tournament.one((v2, rnd, s)) for s in range(100, 106)]
        wins = sum(g["winner"] == "A" for g in games)
        self.assertGreaterEqual(wins, 5)

    def test_viewers_write_html(self):
        flood = os.path.join(ROOT, "bots", "flood_bot.py")
        with tempfile.TemporaryDirectory() as d:
            r = play(cmd(flood), cmd(SAFE), seed=3)
            one = os.path.join(d, "one.html")
            write_html(one, r["replay"], [cmd(flood), cmd(SAFE)])
            games = [tournament.one((flood, SAFE, s)) for s in (10, 11)]
            rep = os.path.join(d, "sub", "report.html")
            write_report(rep, games, "flood_bot", "safe_bot", "2 games")
            for path in (one, rep):
                with open(path) as f:
                    text = f.read()
                self.assertIn("<canvas", text)
                self.assertIn('"frames"', text)


if __name__ == "__main__":
    unittest.main()
