# Experiment Results Summary

## Comparison Table

| Agent 1 | Agent 2 | Board Size | Iterations | Games | Agent 1 Wins | Agent 2 Wins | Draws | Agent 1 Winrate (95% CI) | Agent 2 Winrate (95% CI) | Elo Diff | Avg Time (s) | Avg Sims |
|---------|---------|------------|------------|-------|-------------|--------------|-------|------------------------|------------------------|----------|--------------|----------|
| UCT | RAVE | 3×3 | 20 | 5 | 2 | 3 | 0 | 40.00% [11.76%, 76.93%] | 60.00% [23.07%, 88.24%] | -70.4 | 0.01 | 160 |
| UCT | RAVE | 3×3 | 30 | 5 | 4 | 1 | 0 | 80.00% [37.55%, 96.38%] | 20.00% [3.62%, 62.45%] | +240.8 | 0.01 | 240 |
| UCT | GRAVE | 3×3 | 20 | 5 | 2 | 3 | 0 | 40.00% [11.76%, 76.93%] | 60.00% [23.07%, 88.24%] | -70.4 | 0.01 | 160 |
| UCT | GRAVE | 3×3 | 30 | 5 | 4 | 1 | 0 | 80.00% [37.55%, 96.38%] | 20.00% [3.62%, 62.45%] | +240.8 | 0.01 | 240 |
| RAVE | GRAVE | 3×3 | 20 | 5 | 3 | 2 | 0 | 60.00% [23.07%, 88.24%] | 40.00% [11.76%, 76.93%] | +70.4 | 0.01 | 160 |
| RAVE | GRAVE | 3×3 | 30 | 5 | 2 | 3 | 0 | 40.00% [11.76%, 76.93%] | 60.00% [23.07%, 88.24%] | -70.4 | 0.01 | 240 |

## Notes

- Winrate is calculated as wins / total games
- 95% CI: Wilson confidence interval
- Elo Diff: Estimated Elo difference (positive = Agent 1 stronger)
- Time is average time per game
- Sims is average simulations per game
