# 05 — Cursor Prompts (copy/paste)

Below are *ready-to-paste* prompts for Cursor (or any coding assistant). Use them **in order**.
Assume you are building a clean Python project (no external heavy deps).

---

## Prompt 1 — Repository Skeleton
Create a Python project skeleton with `src/` and `docs/` as described in README.  
Include:
- `pyproject.toml` (or `requirements.txt` if simpler)
- `src/games/hex.py`
- `src/mcts/uct.py`
- `src/eval/match.py`
- minimal unit tests folder `tests/`

Focus on clean interfaces between game and search.

---

## Prompt 2 — Hex Game Implementation
Implement Hex (N×N) with:
- board representation
- legal moves
- apply_move(state, move) returning new state (immutable preferred)
- terminal check + winner detection using BFS/DFS
- serialization for hashing (tuple/bytes)
- unit tests: winner detection and legal move count

Provide docstrings and type hints.

---

## Prompt 3 — UCT Baseline MCTS
Implement UCT MCTS for any game that exposes:
- `legal_moves(state)`
- `next_state(state, move)`
- `is_terminal(state)`
- `reward(state, root_player)` or equivalent

Requirements:
- Node class with N, W, children dict
- select/expand/simulate/backprop loop
- configurable playout budget or time budget
- random playout policy
- deterministic seeding
- unit test: run on tiny Hex board and return a legal move

---

## Prompt 4 — AMAF + RAVE
Extend MCTS to maintain AMAF stats:
- per-node AMAF_N[move], AMAF_W[move]
- update AMAF from simulation trajectory
- implement RAVE blended Q and use it in selection

Add an evaluation script that plays UCT vs RAVE on Hex 5×5 for 50/100/200 iterations per move, 50 games each.

---

## Prompt 5 — GRAVE
Implement GRAVE:
- choose AMAF stats from ancestor with N >= T (threshold)
- integrate into selection (replace local AMAF)
- expose T as a parameter

Update the benchmark to include GRAVE and compare vs UCT and RAVE.

---

## Prompt 6 (optional) — Zobrist Hashing + Transposition Table
Add Zobrist hashing:
- random bitstrings per (cell, player)
- XOR update on move
Create a transposition table mapping hash → node stats.
Integrate TT carefully (ensure correct player-to-move perspective).

Add benchmarks: GRAVE with/without TT.

---

## Prompt 7 (optional) — PUCT with Toy Priors/Value
Implement PUCT:
- a “toy network” function `policy_value(state)` returning (priors dict, value float)
- priors: center bias + small noise (normalize)
- value: heuristic connectivity estimate or 0 baseline

Replace playout with value bootstrap at leaf (or mix with short rollout).
Benchmark PUCT vs GRAVE.

---

## Prompt 8 (optional) — Root Sequential Halving / SHOT
Implement Sequential Halving at the root:
- sample all root moves equally for a small batch
- keep top half, repeat until 1 remains or budget exhausted
Integrate as a wrapper around MCTS iterations.
Benchmark at very small budgets (e.g., 20–100).

---

## Prompt 9 — Experiment Runner + Report Tables
Create a CLI runner:
- choose agent type (UCT/RAVE/GRAVE/PUCT)
- choose board size, budget, number of games, seed
Output CSV with results.
Generate a markdown summary table automatically into `results/summary.md`.

---

## Prompt 10 — Final Report Outline
Generate a report outline:
- rules + representation
- algorithm descriptions (UCT/RAVE/GRAVE/PUCT)
- experiments protocol
- results tables/plots
- discussion + limitations
