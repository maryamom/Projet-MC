# Production Guide

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run Experiments

#### Single Experiment
```bash
python run_experiment.py \
    --agent1 UCT \
    --agent2 RAVE \
    --board-size 5 \
    --iterations 100 \
    --games 50 \
    --seed 42
```

#### Batch Experiments
```bash
python run_batch.py \
    --board-size 5 \
    --iterations 50,100,200,500 \
    --games 50 \
    --seed 42 \
    --output-dir results/production
```

### 3. Generate Reports

```bash
python -m src.eval.report_generator \
    --results-dir results/production \
    --output results/final_report.md
```

## Production Configuration

### Recommended Settings

**Small Budget (< 100 iterations)**:
- Use GRAVE with threshold=50
- Board size: 5×5
- Games: 50-100

**Medium Budget (100-200 iterations)**:
- Use RAVE or GRAVE
- Board size: 5×5 or 7×7
- Games: 50-100

**Large Budget (> 200 iterations)**:
- Use UCT, RAVE, or GRAVE
- Board size: 7×7 or 9×9
- Games: 50-100

### Performance Tuning

**GRAVE Threshold**:
- Small boards (3×3, 5×5): threshold = 50-100
- Medium boards (7×7): threshold = 100-200
- Large boards (9×9+): threshold = 200-500

**PUCT Parameters**:
- `c_puct`: 0.5-2.0 (default: 1.0)
- Higher values = more exploration
- Lower values = more exploitation

## Monitoring

### Key Metrics

1. **Winrate**: Primary performance indicator
2. **Confidence Intervals**: Statistical significance
3. **Elo Difference**: Relative strength
4. **Time per Game**: Performance cost
5. **Simulations**: Computational cost

### Logging

Results are automatically saved to:
- CSV files: Detailed game-by-game results
- Markdown summaries: Aggregated statistics
- Plots: Visual performance comparisons

## Best Practices

1. **Always use alternating starts** for fair comparisons
2. **Run at least 50 games** per configuration for statistical significance
3. **Use fixed seeds** for reproducibility
4. **Track simulations** to understand computational cost
5. **Generate plots** for visual analysis

## Troubleshooting

### High Memory Usage
- Reduce board size
- Clear transposition table between moves
- Use smaller iteration budgets

### Slow Performance
- Reduce iteration budget
- Use smaller board sizes
- Disable transposition table if not needed

### Inconsistent Results
- Increase number of games
- Check random seed consistency
- Verify alternating starts are enabled

## API Usage

### Programmatic Access

```python
from src.eval.runner import run_experiment, aggregate_results
from src.mcts.uct import UCTMCTS
from src.games.hex import HexState

# Run experiment
results = run_experiment('UCT', 'RAVE', 5, 100, 50, seed=42)

# Aggregate results
aggregated = aggregate_results(results)
print(f"Winrate: {aggregated['agent1_winrate']:.2%}")

# Use MCTS directly
state = HexState(5)
mcts = UCTMCTS(random_seed=42)
move = mcts.search(state, iterations=100)
```

## Scaling

### Parallel Execution

For large-scale experiments, consider:
- Running multiple experiments in parallel
- Using different seeds for each process
- Aggregating results afterward

### Cloud Deployment

- Use cloud compute for batch experiments
- Store results in cloud storage
- Generate reports asynchronously

## Support

For issues or questions:
1. Check `TEST_RESULTS.md` for known issues
2. Review `IMPLEMENTATION_SUMMARY.md` for features
3. Consult `docs/` directory for detailed documentation
