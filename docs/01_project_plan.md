# 01 — Project Plan

## Goal
Build a game-playing agent for **Hex** (or Atarigo) using Monte Carlo Tree Search variants from the course, then compare their empirical performance.

## Algorithms to Implement (core)
1. **UCT (baseline MCTS)**
2. **RAVE (AMAF + beta mixing)**
3. **GRAVE (use AMAF from a sufficiently-visited ancestor)**
4. **(Optional) PUCT** using toy priors/value (heuristics or random)

## “All course extras” (recommended/optional)
- **Zobrist hashing + transposition table**
- **Root bandits**: Sequential Halving / SHOT
- **MCTS Solver mode** (mark solved nodes; propagate exact outcomes)

## Engineering Requirements
- Deterministic runs via RNG seeding
- Reproducible experiment scripts
- Clear separation between:
  - game state representation
  - MCTS algorithm
  - evaluation harness

## Success Criteria
- Correctness: rules + winner detection validated by tests
- Strong results: GRAVE and/or PUCT should outperform baseline UCT at small/medium budgets
- Clean evaluation: winrate curves and timing stats are reported

## Implementation Checklist
### Game layer
- [x] Board representation (size N)
- [x] Legal moves generation
- [x] Apply/undo move (or immutable state copy)
- [x] Terminal check + winner detection
- [x] Random agent for baseline comparisons

### MCTS layer
- [x] Node struct: N, W, children, untried moves
- [x] UCT select/expand/simulate/backprop
- [x] AMAF stats per node (RAVE)
- [x] GRAVE ancestor selection threshold
- [x] (Optional) PUCT: priors + value bootstrap
- [x] (Recommended) Zobrist + transposition table
- [x] Sequential Halving / SHOT at root

### Eval layer
- [x] Agent-vs-agent match runner
- [x] Fixed budget per move
- [x] Aggregate stats (winrate, avg time)
- [x] Budget sweep script
- [x] Alternating starting player
- [x] Confidence intervals (Wilson)
- [x] Elo estimation
- [x] Simulation tracking
- [x] Plots and visualization

## Suggested Timeline
- Day 1–2: Hex implementation + tests
- Day 3–4: UCT baseline + sanity games
- Day 5: RAVE
- Day 6: GRAVE
- Day 7: evaluation + plots + report outline
- Extra: PUCT + TT + SHOT
