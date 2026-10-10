"""
HTML viewers for Light Cycles, in the spirit of the CodinGame player.

  write_html(path, replay, cmds)               one game (referee.py --html)
  write_report(path, games, name_a, name_b, sub) a whole tournament: summary,
                                               one tile per game, click a tile
                                               to watch that game

The files are self-contained: no internet, no packages.
"""
import html
import json
import os
import re

COLORS = {"A": "#FF7A1A", "B": "#35C8F0"}


def _short(cmd):
    """'python3 bots/flood_bot.py' -> 'flood_bot'."""
    m = re.search(r"([\w\-]+)\.(py|cpp|out|exe)?['\"]?\s*$", cmd.strip())
    return m.group(1) if m else os.path.basename(cmd.split()[-1])


TEMPLATE = r"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>__TITLE__</title>
<style>
:root{--bg:#0B1530;--panel:#13213F;--line:#24365F;--ink:#E8EEFA;--quiet:#8EA2C8;
--a:#FF7A1A;--b:#35C8F0;--wall:#3A4A72;--cell:#182A52;--bad:#FF4D5E;--draw:#5B6B93}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);
font:14px/1.45 -apple-system,Segoe UI,Helvetica,Arial,sans-serif}
header{display:flex;align-items:center;gap:14px 18px;padding:14px 20px;border-bottom:1px solid var(--line);flex-wrap:wrap}
header h1{font-size:18px;margin:0;font-weight:700}
.tag{font-size:12px;color:var(--quiet)}
.p{display:inline-flex;align-items:center;gap:8px;font-weight:600}
.dot{width:12px;height:12px;border-radius:3px;display:inline-block}
.stats{display:flex;gap:8px;margin-left:auto;flex-wrap:wrap}
.stat{background:var(--panel);border:1px solid var(--line);border-radius:8px;padding:4px 10px;font-weight:600}
.stat small{color:var(--quiet);font-weight:400;margin-right:6px}
main{display:grid;grid-template-columns:__COLS__;gap:16px;padding:16px 20px}
@media (max-width:1000px){main{grid-template-columns:1fr}}
.card{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:14px}
.card h3{font-size:13px;margin:0 0 10px;color:var(--quiet);font-weight:600}
canvas{width:100%;height:auto;display:block;border-radius:6px}
.controls{display:flex;align-items:center;gap:10px;margin-top:12px}
button{background:#1D2F58;color:var(--ink);border:1px solid var(--line);border-radius:6px;
padding:6px 10px;font-size:14px;cursor:pointer;min-width:38px}
button:hover{background:#26396A}button.on{background:var(--ink);color:var(--bg)}
input[type=range]{flex:1;accent-color:var(--a)}
#turn{font-variant-numeric:tabular-nums;min-width:64px;text-align:right;color:var(--quiet)}
select{background:#1D2F58;color:var(--ink);border:1px solid var(--line);border-radius:6px;padding:5px}
#gameinfo{margin-top:10px;color:var(--quiet);min-height:20px}
#gameinfo b{color:var(--ink)}
.console{font:12.5px/1.5 Menlo,Consolas,monospace;max-height:560px;overflow:auto;white-space:pre-wrap}
.t{padding:6px 8px;border-radius:6px;margin-bottom:4px;opacity:.55;cursor:pointer}
.t.cur{background:#1B2C55;opacity:1}
.lbl{color:var(--quiet)}.A{color:var(--a)}.B{color:var(--b)}.dead{color:var(--bad)}
.filters{display:flex;flex-wrap:wrap;gap:6px;margin-bottom:10px}
.filters button{font-size:12px;padding:4px 8px}
.why{display:flex;justify-content:space-between;gap:8px;padding:5px 8px;border-radius:6px;cursor:pointer;margin-bottom:3px}
.why:hover,.why.on{background:#1B2C55}
.why span:last-child{color:var(--quiet);font-variant-numeric:tabular-nums}
.tiles{display:grid;grid-template-columns:repeat(auto-fill,minmax(22px,1fr));gap:4px;margin-top:12px}
.tile{aspect-ratio:1;border-radius:4px;cursor:pointer;border:2px solid transparent}
.tile.dim{opacity:.15}.tile.sel{border-color:#fff}
.legend{display:flex;gap:12px;font-size:12px;color:var(--quiet);margin-top:8px;flex-wrap:wrap}
</style></head><body>
<header>
  <h1>__TITLE__</h1><span class="tag">__SUB__</span>
  <span class="p"><span class="dot" style="background:var(--a)"></span>A: __NAME_A__</span>
  <span class="p"><span class="dot" style="background:var(--b)"></span>B: __NAME_B__</span>
  <div class="stats" id="stats"></div>
</header>
<main>
  <section class="card" id="picker" style="__PICKER_STYLE__">
    <h3>Games: click one to watch it</h3>
    <div class="filters" id="filters"></div>
    <h3 style="margin-top:6px">How A died (click to filter)</h3>
    <div id="whys"></div>
    <div class="tiles" id="tiles"></div>
    <div class="legend"><span><span class="dot" style="background:var(--a)"></span> A won</span>
      <span><span class="dot" style="background:var(--b)"></span> B won</span>
      <span><span class="dot" style="background:var(--draw)"></span> draw</span></div>
  </section>
  <section class="card">
    <canvas id="c"></canvas>
    <div class="controls">
      <button id="first" title="first turn">&#x23EE;</button>
      <button id="prev" title="previous turn (left arrow)">&#x25C0;</button>
      <button id="play" title="play / pause (space)">&#x25B6;</button>
      <button id="next" title="next turn (right arrow)">&#x25B6;&#x25B6;</button>
      <input id="slider" type="range" min="0" value="0">
      <span id="turn"></span>
      <select id="speed" title="speed"><option value="400">0.5x</option><option value="200" selected>1x</option><option value="90">2x</option><option value="40">4x</option></select>
    </div>
    <div id="gameinfo"></div>
  </section>
  <section class="card console" id="log"></section>
</main>
<script>
const D = __DATA__;
const MULTI = D.games.length > 1;
const c = document.getElementById("c"), ctx = c.getContext("2d");
const S = 40, PAD = 2;
const css = n => getComputedStyle(document.documentElement).getPropertyValue(n).trim();
const COL = {A: css("--a"), B: css("--b"), wall: css("--wall"), cell: css("--cell"), bad: css("--bad"), draw: css("--draw")};
const slider = document.getElementById("slider");
let G = null, T = 0, t = 0, timer = null, filter = {kind: "all", why: null};

const letter = i => (i === G.aIdx ? "A" : "B");
function rect(x, y, color, alpha) {
  ctx.globalAlpha = alpha; ctx.fillStyle = color;
  const X = x * S + PAD, Y = y * S + PAD, W = S - 2 * PAD;
  ctx.beginPath(); ctx.roundRect ? ctx.roundRect(X, Y, W, W, 6) : ctx.rect(X, Y, W, W); ctx.fill();
  ctx.globalAlpha = 1;
}
function cross(x, y) {
  ctx.strokeStyle = COL.bad; ctx.lineWidth = 5; const a = x * S + 9, b = y * S + 9, e = S - 18;
  ctx.beginPath(); ctx.moveTo(a, b); ctx.lineTo(a + e, b + e); ctx.moveTo(a + e, b); ctx.lineTo(a, b + e); ctx.stroke();
}
function draw() {
  const R = G.r;
  ctx.clearRect(0, 0, c.width, c.height);
  for (let y = 0; y < R.h; y++) for (let x = 0; x < R.w; x++) rect(x, y, COL.cell, 1);
  for (const [x, y] of R.walls) rect(x, y, COL.wall, 1);
  const heads = [R.start[0], R.start[1]];
  for (let i = 0; i < 2; i++) rect(R.start[i][0], R.start[i][1], COL[letter(i)], 0.45);
  for (let k = 0; k < t; k++) {
    const f = R.frames[k];
    for (let i = 0; i < 2; i++) if (f.a[i]) { rect(f.p[i][0], f.p[i][1], COL[letter(i)], 0.45); heads[i] = f.p[i]; }
  }
  for (let i = 0; i < 2; i++) {
    const [x, y] = heads[i];
    rect(x, y, COL[letter(i)], 1);
    ctx.fillStyle = "#0B1530"; ctx.font = "bold 20px Helvetica, Arial"; ctx.textAlign = "center"; ctx.textBaseline = "middle";
    ctx.fillText(letter(i), x * S + S / 2, y * S + S / 2 + 1);
  }
  if (t > 0) { const f = R.frames[t - 1]; for (let i = 0; i < 2; i++) if (f.x[i]) {
    const [x, y] = f.x[i]; if (x >= 0 && y >= 0 && x < R.w && y < R.h) cross(x, y); } }
  slider.value = t;
  document.getElementById("turn").textContent = t + " / " + T;
  document.querySelectorAll(".t").forEach((el, k) => el.classList.toggle("cur", k === t - 1));
  const cur = document.querySelector(".t.cur"); if (cur) cur.scrollIntoView({block: "nearest"});
  const info = document.getElementById("gameinfo");
  const res = G.res === "D" ? "Draw" : G.res + " wins";
  const why = [G.why[0] ? "A: " + G.why[0] : "", G.why[1] ? "B: " + G.why[1] : ""].filter(Boolean).join(" · ");
  info.innerHTML = (MULTI ? "Seed <b>" + G.seed + "</b> · " : "") + (t === T ? "<b>" + res + "</b> after " + T + " turns" + (why ? " · " + why : "") : "turn " + t + " of " + T);
}
function buildLog() {
  const log = document.getElementById("log"); log.innerHTML = "<h3>Console output</h3>";
  G.r.frames.forEach((f, k) => {
    const d = document.createElement("div"); d.className = "t";
    let s = '<span class="lbl">Turn ' + (k + 1) + '  Standard Output Stream:</span>\n';
    for (const i of [G.aIdx, 1 - G.aIdx]) s += '<span class="' + letter(i) + '">' + letter(i) + " &gt; " + (f.m[i] || "(no answer)") + "</span>\n";
    const prev = k ? G.r.frames[k - 1].a : [true, true];
    for (const i of [G.aIdx, 1 - G.aIdx]) if (prev[i] && !f.a[i]) s += '<span class="dead">' + letter(i) + " was eliminated: " + G.why[letter(i) === "A" ? 0 : 1] + "</span>\n";
    d.innerHTML = s; d.onclick = () => { stop(); t = k + 1; draw(); }; log.appendChild(d);
  });
}
function load(k, autoplay) {
  stop(); G = D.games[k]; T = G.r.frames.length; t = 0;
  c.width = G.r.w * S; c.height = G.r.h * S; slider.max = T;
  buildLog(); draw();
  document.querySelectorAll(".tile").forEach((el, j) => el.classList.toggle("sel", j === k));
  if (autoplay) play();
}
function stop() { clearInterval(timer); timer = null; document.getElementById("play").innerHTML = "&#x25B6;"; }
function play() {
  if (timer) return stop();
  if (t >= T) t = 0;
  document.getElementById("play").innerHTML = "&#x23F8;";
  timer = setInterval(() => { if (t >= T) return stop(); t++; draw(); }, +document.getElementById("speed").value);
}
function matches(g) {
  if (filter.why) return g.why[0] === filter.why;
  if (filter.kind === "won") return g.res === "A";
  if (filter.kind === "lost") return g.res === "B";
  if (filter.kind === "draw") return g.res === "D";
  return true;
}
function refreshFilter() {
  document.querySelectorAll(".tile").forEach((el, j) => el.classList.toggle("dim", !matches(D.games[j])));
  document.querySelectorAll(".filters button").forEach(b => b.classList.toggle("on", !filter.why && b.dataset.k === filter.kind));
  document.querySelectorAll(".why").forEach(w => w.classList.toggle("on", w.dataset.w === filter.why));
}
function buildPicker() {
  const n = D.games.length, cnt = {A: 0, B: 0, D: 0}, whys = {};
  D.games.forEach(g => { cnt[g.res]++; if (g.why[0]) whys[g.why[0]] = (whys[g.why[0]] || 0) + 1; });
  const v = 100 * (cnt.A + 0.5 * cnt.D) / n, f = Math.floor(v);   // round half to even, like Python
  const score = Math.abs(v - f - 0.5) < 1e-9 ? (f % 2 === 0 ? f : f + 1) : Math.round(v);
  document.getElementById("stats").innerHTML =
    '<span class="stat"><small>A wins</small>' + cnt.A + '</span><span class="stat"><small>B wins</small>' + cnt.B +
    '</span><span class="stat"><small>draws</small>' + cnt.D + '</span><span class="stat"><small>A score</small>' + score + '%</span>';
  const fl = document.getElementById("filters");
  [["all", "All " + n], ["won", "A won " + cnt.A], ["lost", "A lost " + cnt.B], ["draw", "Draws " + cnt.D]].forEach(([k, lbl]) => {
    const b = document.createElement("button"); b.dataset.k = k; b.textContent = lbl;
    b.onclick = () => { filter = {kind: k, why: null}; refreshFilter(); }; fl.appendChild(b);
  });
  const wl = document.getElementById("whys");
  const ws = Object.entries(whys).sort((a, b) => b[1] - a[1]);
  if (!ws.length) wl.innerHTML = '<div class="why"><span>A never died</span><span></span></div>';
  ws.forEach(([w, k]) => {
    const d = document.createElement("div"); d.className = "why"; d.dataset.w = w;
    d.innerHTML = "<span>" + w + "</span><span>" + k + "</span>";
    d.onclick = () => { filter = {kind: "all", why: filter.why === w ? null : w}; refreshFilter(); }; wl.appendChild(d);
  });
  const tl = document.getElementById("tiles");
  D.games.forEach((g, k) => {
    const d = document.createElement("div"); d.className = "tile";
    d.style.background = g.res === "A" ? COL.A : g.res === "B" ? COL.B : COL.draw;
    d.title = "seed " + g.seed + ": " + (g.res === "D" ? "draw" : g.res + " won") + " in " + g.r.frames.length + " turns";
    d.onclick = () => load(k, true); tl.appendChild(d);
  });
  refreshFilter();
}
document.getElementById("play").onclick = play;
document.getElementById("next").onclick = () => { stop(); t = Math.min(T, t + 1); draw(); };
document.getElementById("prev").onclick = () => { stop(); t = Math.max(0, t - 1); draw(); };
document.getElementById("first").onclick = () => { stop(); t = 0; draw(); };
document.getElementById("speed").onchange = () => { if (timer) { stop(); play(); } };
slider.oninput = () => { stop(); t = +slider.value; draw(); };
document.addEventListener("keydown", e => {
  if (e.code === "Space") { e.preventDefault(); play(); }
  if (e.code === "ArrowRight") document.getElementById("next").click();
  if (e.code === "ArrowLeft") document.getElementById("prev").click();
});
if (MULTI) buildPicker();
const still = location.hash.includes("still");
load(0, !still && !MULTI);
</script></body></html>
"""


def _game(replay, seed, a_idx, winner, why):
    """Pack one game for the viewer. winner is 'A', 'B' or 'D'; why is [A's death, B's death]."""
    return {"seed": seed, "aIdx": a_idx, "res": winner, "why": why,
            "r": {k: replay[k] for k in ("w", "h", "walls", "start", "frames")}}


def _render(path, title, sub, name_a, name_b, games):
    multi = len(games) > 1
    out = (TEMPLATE
           .replace("__COLS__", "minmax(240px,300px) minmax(0,1.6fr) minmax(240px,1fr)" if multi
                    else "minmax(0,1.6fr) minmax(260px,1fr)")
           .replace("__PICKER_STYLE__", "" if multi else "display:none")
           .replace("__TITLE__", html.escape(title)).replace("__SUB__", html.escape(sub))
           .replace("__NAME_A__", html.escape(name_a)).replace("__NAME_B__", html.escape(name_b))
           .replace("__DATA__", json.dumps({"games": games}, separators=(",", ":"))))
    folder = os.path.dirname(path)
    if folder:
        os.makedirs(folder, exist_ok=True)
    with open(path, "w") as f:
        f.write(out)


def write_html(path, replay, cmds):
    """One game. Player 0 (the first command) is A."""
    res = {0: "A", 1: "B", -1: "D"}[replay["result"]]
    game = _game(replay, replay["seed"], 0, res, list(replay["reason"]))
    _render(path, "Light Cycles", f"seed {replay['seed']} · {replay['w']}×{replay['h']}",
            _short(cmds[0]), _short(cmds[1]), [game])


def write_report(path, games, name_a, name_b, sub):
    """A tournament: `games` are the dicts returned by tournament.one()."""
    packed = [_game(g["replay"], g["seed"], g["a_idx"],
                    {"A": "A", "B": "B", "draw": "D"}[g["winner"]], list(g["reasons"]))
              for g in games]
    _render(path, f"{name_a} vs {name_b}", sub, name_a, name_b, packed)
