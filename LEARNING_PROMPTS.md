# Coach prompts for locked-workspace practice

For practice before the contest only. In the locked-workspace tasks, AI is not
allowed and paste is disabled, so the goal of every prompt here is to make
YOU able to solve the next problem alone.

Tip: save the first prompt as a custom instruction or project prompt in your
AI tool so every practice chat starts in coach mode.

## 1. Coach mode (instead of "solve this")

```
I'm training for a contest where AI and paste are disabled. Don't write code.
Ask me one question at a time that leads me to the key idea. If I'm stuck
twice, give the smallest hint you can.

Problem: <paste statement>
```

## 2. The hint ladder

```
Give me hint level 1 only. Wait for my answer before level 2.
Levels: 1 = what kind of problem it is, 2 = the key observation about the
input, 3 = the technique and why the constraints allow it, 4 = pseudocode in
plain words. Never give code.
```

## 3. Debug with evidence (instead of "why is my code wrong?")

```
Input: <failing case>
Expected: <x>
My output: <y>
Point to the first line where my logic goes wrong and explain why. Don't fix it.

<your code>
```

## 4. Break my solution (instead of "is my solution correct?")

```
Try to break my solution. Give me 5 small inputs most likely to fail it, with
expected outputs. Then write a brute-force version I can compare against on
random tests.
```

Later, write the brute force yourself: on contest day nobody writes it for you.

## 5. Recognition drill (instead of "explain BFS")

```
Give me 5 short problem statements: 3 solved by <technique>, 2 that look like
it but aren't. Don't tell me which. I'll classify them and say what in the
constraints gave it away.
```

## 6. Complexity check

```
Constraints: n ≤ <N>, time limit <T> s. My idea is <describe it>.
What is its complexity? Will it pass? If not, what is the bottleneck?
Don't give me the faster solution, only tell me where to look.
```

## 7. Post-mortem

```
I solved this with <k> hints. Ask me 3 questions to check I understand why
the solution works.
```

## 8. Quiz after a CS Academy lesson

```
I just read the CS Academy lesson on <topic> (csacademy.com/lessons).
Quiz me with 5 questions, one at a time, from easy to hard. Wait for my
answer each time and tell me what I got wrong.
```

## The practice loop

1. Try alone for 25 minutes, paper first, no AI.
2. Ask for one hint (the next rung only).
3. Code it yourself, typing every line.
4. Break it: edge cases and a brute-force stress test.
5. Post-mortem: what in the statement should have told me?
6. Redo it in 3 days, from scratch, no AI.
