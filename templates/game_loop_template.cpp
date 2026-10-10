// Game-loop skeleton for stdin/stdout bot tasks (CodinGame / IEEEXtreme game-type).
// Reads the Light Cycles protocol from this kit; adapt the parsing to your task's SPEC.
#include <bits/stdc++.h>
using namespace std;

int main() {
    // Fast I/O is fine in interactive tasks as long as every answer is flushed (endl does it).
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int W, H, me;
    if (!(cin >> W >> H >> me)) return 0;
    while (true) {
        int x[2], y[2];
        if (!(cin >> x[0] >> y[0] >> x[1] >> y[1])) return 0;   // referee closed: game over
        vector<string> g(H);
        for (auto& row : g) cin >> row;                         // read the WHOLE turn input

        auto t0 = chrono::steady_clock::now();
        auto elapsed_ms = [&] {
            return chrono::duration<double, milli>(chrono::steady_clock::now() - t0).count();
        };

        const char* names[] = {"UP", "DOWN", "LEFT", "RIGHT"};
        int dx[] = {0, 0, -1, 1}, dy[] = {-1, 1, 0, 0};
        string best = "UP";
        for (int d = 0; d < 4 && elapsed_ms() < 40; d++) {      // stay well under the limit
            int nx = x[me] + dx[d], ny = y[me] + dy[d];
            if (nx >= 0 && nx < W && ny >= 0 && ny < H && g[ny][nx] == '.') { best = names[d]; break; }
        }
        cerr << "turn took " << elapsed_ms() << " ms\n";        // debug goes to stderr
        cout << best << endl;                                   // endl flushes
    }
}
