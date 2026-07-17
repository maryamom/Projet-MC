"""Advanced analysis tools for experiment results."""

import csv
import os
from typing import List, Dict, Tuple
from collections import defaultdict
import glob


def load_all_results(results_dir: str) -> List[Dict]:
    """Load all results from CSV files in directory.
    
    Args:
        results_dir: Directory containing CSV files
        
    Returns:
        List of all result dictionaries
    """
    all_results = []
    csv_files = glob.glob(os.path.join(results_dir, '*.csv'))
    
    for csv_file in csv_files:
        with open(csv_file, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Convert types
                for key in ['board_size', 'iterations', 'seed', 'agent1_wins', 
                           'agent2_wins', 'draws', 'time', 'simulations']:
                    if key in row:
                        try:
                            row[key] = int(row[key]) if row[key] else 0
                        except ValueError:
                            row[key] = 0
                for key in ['time']:
                    if key in row:
                        try:
                            row[key] = float(row[key]) if row[key] else 0.0
                        except ValueError:
                            row[key] = 0.0
                all_results.append(row)
    
    return all_results


def analyze_algorithm_performance(results: List[Dict]) -> Dict:
    """Analyze overall performance of each algorithm.
    
    Args:
        results: List of result dictionaries
        
    Returns:
        Dictionary with algorithm statistics
    """
    from .runner import aggregate_results
    
    # Group by algorithm pairs and iterations
    grouped = defaultdict(list)
    for r in results:
        key = (r['agent1_type'], r['agent2_type'], r['iterations'])
        grouped[key].append(r)
    
    # Aggregate each group
    aggregated = []
    for (a1, a2, iters), group_results in grouped.items():
        agg = aggregate_results(group_results)
        aggregated.append(agg)
    
    # Calculate per-algorithm statistics
    algo_stats = defaultdict(lambda: {'wins': 0, 'games': 0, 'total_time': 0.0})
    
    for agg in aggregated:
        a1 = agg['agent1_type']
        a2 = agg['agent2_type']
        
        algo_stats[a1]['wins'] += agg['agent1_wins']
        algo_stats[a1]['games'] += agg['num_games']
        algo_stats[a1]['total_time'] += agg['total_time']
        
        algo_stats[a2]['wins'] += agg['agent2_wins']
        algo_stats[a2]['games'] += agg['num_games']
        algo_stats[a2]['total_time'] += agg['total_time']
    
    # Calculate winrates and averages
    performance = {}
    for algo, stats in algo_stats.items():
        performance[algo] = {
            'winrate': stats['wins'] / stats['games'] if stats['games'] > 0 else 0,
            'total_wins': stats['wins'],
            'total_games': stats['games'],
            'avg_time': stats['total_time'] / stats['games'] if stats['games'] > 0 else 0
        }
    
    return performance


def analyze_budget_scaling(results: List[Dict]) -> Dict:
    """Analyze how performance scales with iteration budget.
    
    Args:
        results: List of result dictionaries
        
    Returns:
        Dictionary mapping iterations to performance metrics
    """
    from .runner import aggregate_results
    
    # Group by iterations
    by_iterations = defaultdict(list)
    for r in results:
        by_iterations[r['iterations']].append(r)
    
    scaling = {}
    for iterations, group_results in sorted(by_iterations.items()):
        # Aggregate by algorithm pair
        pairs = defaultdict(list)
        for r in group_results:
            key = (r['agent1_type'], r['agent2_type'])
            pairs[key].append(r)
        
        pair_results = []
        for pair_results_list in pairs.values():
            agg = aggregate_results(pair_results_list)
            pair_results.append(agg)
        
        scaling[iterations] = {
            'num_configurations': len(pair_results),
            'avg_winrate_spread': sum(abs(r['agent1_winrate'] - 0.5) for r in pair_results) / len(pair_results) if pair_results else 0,
            'avg_time': sum(r['avg_time'] for r in pair_results) / len(pair_results) if pair_results else 0
        }
    
    return scaling


def generate_statistical_summary(results: List[Dict]) -> str:
    """Generate statistical summary of results.
    
    Args:
        results: List of result dictionaries
        
    Returns:
        Formatted summary string
    """
    from .runner import aggregate_results
    
    # Aggregate all results
    aggregated = aggregate_results(results)
    
    summary = []
    summary.append("## Statistical Summary\n\n")
    summary.append(f"- **Total Games**: {aggregated['num_games']}\n")
    summary.append(f"- **Agent 1 ({aggregated['agent1_type']}) Winrate**: {aggregated['agent1_winrate']:.2%}\n")
    summary.append(f"- **Agent 2 ({aggregated['agent2_type']}) Winrate**: {aggregated['agent2_winrate']:.2%}\n")
    summary.append(f"- **Elo Difference**: {aggregated.get('elo_difference', 0):+.1f}\n")
    summary.append(f"- **Average Time per Game**: {aggregated['avg_time']:.3f}s\n")
    summary.append(f"- **Average Simulations per Game**: {aggregated.get('avg_simulations', 0):.0f}\n")
    summary.append(f"\n### Confidence Intervals (95%)\n\n")
    summary.append(f"- **Agent 1**: [{aggregated.get('agent1_ci_lower', 0):.2%}, {aggregated.get('agent1_ci_upper', 1):.2%}]\n")
    summary.append(f"- **Agent 2**: [{aggregated.get('agent2_ci_lower', 0):.2%}, {aggregated.get('agent2_ci_upper', 1):.2%}]\n")
    
    return ''.join(summary)


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Analyze experiment results')
    parser.add_argument('--results-dir', type=str, default='results/large_scale',
                       help='Results directory')
    parser.add_argument('--output', type=str, default='results/analysis.md',
                       help='Output analysis file')
    
    args = parser.parse_args()
    
    results = load_all_results(args.results_dir)
    
    if not results:
        print(f"No results found in {args.results_dir}")
        exit(1)
    
    # Generate analysis
    performance = analyze_algorithm_performance(results)
    scaling = analyze_budget_scaling(results)
    
    # Write analysis
    os.makedirs(os.path.dirname(args.output) if os.path.dirname(args.output) else '.', exist_ok=True)
    
    with open(args.output, 'w') as f:
        f.write("# Experiment Analysis\n\n")
        
        f.write("## Algorithm Performance\n\n")
        f.write("| Algorithm | Winrate | Total Wins | Total Games | Avg Time (s) |\n")
        f.write("|-----------|---------|------------|-------------|--------------|\n")
        for algo, stats in sorted(performance.items(), key=lambda x: x[1]['winrate'], reverse=True):
            f.write(f"| {algo} | {stats['winrate']:.2%} | {stats['total_wins']} | ")
            f.write(f"{stats['total_games']} | {stats['avg_time']:.3f} |\n")
        
        f.write("\n## Budget Scaling Analysis\n\n")
        f.write("| Iterations | Configurations | Avg Winrate Spread | Avg Time (s) |\n")
        f.write("|------------|----------------|-------------------|--------------|\n")
        for iters, stats in sorted(scaling.items()):
            f.write(f"| {iters} | {stats['num_configurations']} | ")
            f.write(f"{stats['avg_winrate_spread']:.3f} | {stats['avg_time']:.3f} |\n")
        
        f.write("\n")
        f.write(generate_statistical_summary(results))
    
    print(f"Analysis saved to {args.output}")
