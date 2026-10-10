#!/usr/bin/env bash
# Live demo for the "Live: Light Cycles" slide. Press Enter before each step.
# Every step writes its own HTML page into reports/ and opens it in Chrome
# (falls back to your default browser if Chrome isn't installed).
#
#   ./demo.sh                 run it
#   WORKERS=8 ./demo.sh       use more CPU cores
#   NO_OPEN=1 ./demo.sh       don't open browser tabs
cd "$(dirname "$0")" || exit 1
PY="${PYTHON:-python3}"
W="${WORKERS:-4}"
mkdir -p reports

pause() { echo; read -r -p ">> $1   [Enter to run, Ctrl+C to stop] " _; }
run()   { printf '$'; printf ' %q' "$@"; echo; "$@"; }
show() {
  [ -n "$NO_OPEN" ] && { echo "Report: $1"; return; }
  if [ "$(uname)" = "Darwin" ]; then
    open -a "Google Chrome" "$1" 2>/dev/null || open "$1"
  elif command -v google-chrome >/dev/null 2>&1; then google-chrome "$1" >/dev/null 2>&1 &
  elif command -v chromium >/dev/null 2>&1; then chromium "$1" >/dev/null 2>&1 &
  elif command -v xdg-open >/dev/null 2>&1; then xdg-open "$1"
  else echo "Open $1 in your browser."; fi
}

pause "1. Watch one game: flood (A, orange) vs safe (B, blue)"
run "$PY" referee.py "$PY bots/flood_bot.py" "$PY bots/safe_bot.py" --seed 3 --html reports/1_one_game.html
show reports/1_one_game.html

pause "2a. Ladder: safe vs random, 200 games on fresh boards"
run "$PY" tournament.py bots/safe_bot.py bots/random_bot.py --games 200 --offset 5000 --workers "$W" --html reports/2a_safe_vs_random.html
show reports/2a_safe_vs_random.html

pause "2b. Ladder: flood vs safe"
run "$PY" tournament.py bots/flood_bot.py bots/safe_bot.py --games 200 --offset 5000 --workers "$W" --html reports/2b_flood_vs_safe.html
show reports/2b_flood_vs_safe.html

pause "3a. The surprise, part 1: voronoi v1 beats flood head to head"
run "$PY" tournament.py bots/voronoi_bot.py bots/flood_bot.py --games 200 --workers "$W" --html reports/3a_voronoi_vs_flood.html
show reports/3a_voronoi_vs_flood.html

pause "3b. The surprise, part 2: but v1 does WORSE against safe than flood did. Read 'How A died'."
run "$PY" tournament.py bots/voronoi_bot.py bots/safe_bot.py --games 200 --offset 5000 --workers "$W" --html reports/3b_voronoi_vs_safe.html
show reports/3b_voronoi_vs_safe.html
echo
echo "In the report, click 'A lost' to watch the games voronoi lost."
echo "Then paste the terminal output above into your AI with the prompt from the slides."

pause "4. The fix (v2 = dead-end filter) against safe"
run "$PY" tournament.py bots/voronoi_v2_bot.py bots/safe_bot.py --games 200 --offset 5000 --workers "$W" --html reports/4_v2_vs_safe.html
show reports/4_v2_vs_safe.html

pause "5. Gauntlet: v2 against every bot in bots/ (100 games each)"
run "$PY" gauntlet.py bots/voronoi_v2_bot.py --games 100 --offset 5000 --workers "$W"

pause "6. Bonus: the agents' bots head to head, aggressor vs endgame"
run "$PY" tournament.py bots/v3_aggressor_bot.py bots/v3_endgame_bot.py --games 200 --offset 5000 --workers "$W" --html reports/6_aggressor_vs_endgame.html
show reports/6_aggressor_vs_endgame.html

echo
echo "Done. All reports are in the reports/ folder."
