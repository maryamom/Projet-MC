"""Batch experiment runner for multiple configurations."""

import argparse
import os
from typing import List, Dict
from .runner import run_experiment, aggregate_results, generate_summary_markdown
from .plots import plot_winrate_vs_budget, plot_time_vs_budget, plot_performance_curves


def run_batch_experiments(board_size: int = 5,
                          iterations_list: List[int] = [50, 100, 200],
                          num_games: int = 50,
                          seed: int = 42,
                          threshold: int = 100,
                          output_dir: str = 'results'):
    """Run batch experiments comparing UCT, RAVE, and GRAVE.
    
    Args:
        board_size: Hex board size
        iterations_list: List of iteration budgets to test
        num_games: Number of games per configuration
        seed: Random seed
        threshold: GRAVE threshold T
        output_dir: Output directory for results
    """
    os.makedirs(output_dir, exist_ok=True)
    
    all_aggregated = []
    
    # Compare UCT vs RAVE
    print("=" * 70)
    print("UCT vs RAVE")
    print("=" * 70)
    for iterations in iterations_list:
        csv_file = os.path.join(output_dir, f'uct_vs_rave_{iterations}.csv')
        results = run_experiment('UCT', 'RAVE', board_size, iterations,
                                num_games, seed, output_csv=csv_file)
        aggregated = aggregate_results(results)
        aggregated['comparison'] = 'UCT_vs_RAVE'
        all_aggregated.append(aggregated)
    
    # Compare UCT vs GRAVE
    print("\n" + "=" * 70)
    print("UCT vs GRAVE")
    print("=" * 70)
    for iterations in iterations_list:
        csv_file = os.path.join(output_dir, f'uct_vs_grave_{iterations}.csv')
        results = run_experiment('UCT', 'GRAVE', board_size, iterations,
                                num_games, seed, output_csv=csv_file,
                                threshold=threshold)
        aggregated = aggregate_results(results)
        aggregated['comparison'] = 'UCT_vs_GRAVE'
        all_aggregated.append(aggregated)
    
    # Compare RAVE vs GRAVE
    print("\n" + "=" * 70)
    print("RAVE vs GRAVE")
    print("=" * 70)
    for iterations in iterations_list:
        csv_file = os.path.join(output_dir, f'rave_vs_grave_{iterations}.csv')
        results = run_experiment('RAVE', 'GRAVE', board_size, iterations,
                                num_games, seed, output_csv=csv_file,
                                threshold=threshold)
        aggregated = aggregate_results(results)
        aggregated['comparison'] = 'RAVE_vs_GRAVE'
        all_aggregated.append(aggregated)
    
    # Generate summary
    summary_file = os.path.join(output_dir, 'summary.md')
    generate_summary_markdown(all_aggregated, summary_file)
    print(f"\nSummary saved to {summary_file}")
    
    # Generate plots
    print("\nGenerating plots...")
    
    # Group results by comparison type
    for comparison in ['UCT_vs_RAVE', 'UCT_vs_GRAVE', 'RAVE_vs_GRAVE']:
        comp_results = [r for r in all_aggregated if r.get('comparison') == comparison]
        if comp_results:
            plot_file = os.path.join(output_dir, f'{comparison.lower()}_curves.png')
            plot_winrate_vs_budget(comp_results, plot_file,
                                  agent1_name=comp_results[0]['agent1_type'],
                                  agent2_name=comp_results[0]['agent2_type'])
    
    # Overall performance curves
    plot_file = os.path.join(output_dir, 'performance_curves.png')
    plot_performance_curves(all_aggregated, plot_file)
    print(f"Plots saved to {output_dir}")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description='Run batch MCTS experiments')
    parser.add_argument('--board-size', type=int, default=5,
                       help='Hex board size (default: 5)')
    parser.add_argument('--iterations', type=str, default='50,100,200',
                       help='Comma-separated list of iteration budgets (default: 50,100,200)')
    parser.add_argument('--games', type=int, default=50,
                       help='Number of games per configuration (default: 50)')
    parser.add_argument('--seed', type=int, default=42,
                       help='Random seed (default: 42)')
    parser.add_argument('--threshold', type=int, default=100,
                       help='GRAVE threshold T (default: 100)')
    parser.add_argument('--output-dir', type=str, default='results',
                       help='Output directory (default: results)')
    
    args = parser.parse_args()
    
    iterations_list = [int(x.strip()) for x in args.iterations.split(',')]
    
    run_batch_experiments(
        args.board_size, iterations_list, args.games,
        args.seed, args.threshold, args.output_dir
    )


if __name__ == '__main__':
    main()
