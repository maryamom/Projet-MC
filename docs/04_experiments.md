# 04 — Experiments & Metrics

## Agents to Compare
Minimum:
- UCT
- UCT + RAVE
- UCT + GRAVE
Optional:
- PUCT (toy priors/value)
- +Transposition Table (TT) variants
- +SHOT at root variants

## Controlled Variables
- Board size: start with **Hex 5×5** then 7×7 or 9×9 if time allows
- Budget per move: e.g. **50, 100, 200, 500, 1000** iterations (or playouts)
- RNG seed: fixed list of seeds for reproducibility
- Same time limit or same iteration count (choose one)

## Match Protocol
For each pair (A, B):
- Play **K games** (e.g., 200) at each budget
- Alternate who starts (A first in half games)
- Record:
  - wins for A and B
  - avg time per move (or per game)
  - total simulations executed

## Metrics
- **Winrate** (primary): W / K
- **Confidence interval** (optional): Wilson interval
- **Speed**: avg ms/move
- **Performance curve**: winrate vs budget
- Optional: Elo estimate (e.g., logistic fit from match results)

## Reporting Template
For each budget:
- Table: winrate(A vs B), time/move, simulations/move
- Plot: winrate vs budget

## Sanity Checks
- UCT vs random: should beat random
- Symmetry tests: swapping colors should not break logic
- Winner detection correctness with handcrafted positions
