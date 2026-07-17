# Project B — Hex (or Atarigo): UCT vs RAVE vs GRAVE vs (optional) PUCT

This project implements and compares Monte Carlo Tree Search variants taught in **MonteCarlo (1)**:
- **UCT** (baseline MCTS)
- **AMAF/RAVE**
- **GRAVE**
- **(Optional) PUCT** with a *toy* policy/value “network” (heuristics or random priors)
- (Recommended add-ons from the course, if you want “all”): **Zobrist hashing + transposition table**, **Sequential Halving / SHOT at the root**, and a small **MCTS Solver** mode.

You will evaluate algorithms on **Hex** (recommended) or **Atarigo** (optional alternative).

---

## Why Hex?
- Perfect information, deterministic, no draws (on standard boards)
- Large branching factor → MCTS improvements are visible
- Simple rules, easy to implement, easy to benchmark

Atarigo is also fine if your course explicitly cited it, but Hex tends to be smoother for experiments.

---

## Expected Deliverables
1. **Working engine** for Hex (and optionally Atarigo)
2. **MCTS implementations**: UCT, RAVE, GRAVE, (optional) PUCT
3. **Experiment harness**: run many games, fixed budgets, collect winrate & time
4. **Report**: algorithm descriptions + results + discussion

---

## Recommended Repo Structure
```
project/
  src/
    games/
      hex.py
      atarigo.py               # optional
    mcts/
      node.py
      uct.py
      rave.py
      grave.py
      puct.py                 # optional
      transposition.py        # zobrist + TT
      root_bandits.py         # optional: SHOT/Sequential Halving
    eval/
      match.py
      benchmarks.py
      plots.py                # optional
  docs/
    01_project_plan.md
    02_game_specs.md
    03_algorithms.md
    04_experiments.md
    05_cursor_prompts.md
  README.md
```

---

## Quick Milestone Plan (1–2 weeks)
- **M1**: Implement Hex + legal moves + terminal check + winner detection
- **M2**: Implement UCT baseline + random playout policy
- **M3**: Add AMAF stats + RAVE selection, compare vs UCT
- **M4**: Add GRAVE, compare vs UCT/RAVE
- **M5 (optional)**: Add PUCT with toy priors/value; compare vs GRAVE
- **M6 (recommended)**: Add Zobrist + transposition table
- **M7 (optional)**: Add SHOT at the root; compare at small budgets

---

## Evaluation (minimum)
- **Winrate** at fixed playout budgets (e.g., 50/100/200/500/1000 playouts per move)
- **Performance vs budget curve**
- **CPU time per move / per game**
- Optional: Elo estimate via many matches

See `docs/04_experiments.md` for a concrete protocol.

---

## Quick Start

### Running a Single Experiment

```bash
python run_experiment.py --agent1 UCT --agent2 RAVE --board-size 5 --iterations 100 --games 50
```

### Running Batch Experiments

```bash
python run_batch.py --board-size 5 --iterations 50,100,200 --games 50
```

### Running Tests

```bash
python -m pytest tests/ -v
```

### Project Structure

- `src/games/hex.py` - Hex game implementation
- `src/mcts/uct.py` - UCT MCTS algorithm
- `src/mcts/rave.py` - RAVE MCTS algorithm  
- `src/mcts/grave.py` - GRAVE MCTS algorithm
- `src/eval/runner.py` - CLI experiment runner
- `src/eval/batch_runner.py` - Batch experiment runner
- `tests/` - Unit tests

### Example Usage

```python
from src.games.hex import HexState
from src.mcts.uct import UCTMCTS

# Create initial state
state = HexState(5)

# Create MCTS agent
mcts = UCTMCTS(random_seed=42)

# Search for best move
move = mcts.search(state, iterations=100)
print(f"Best move: {move}")
```
