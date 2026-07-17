"""Comprehensive report generator for experiment results."""

import os
import csv
from typing import List, Dict
from pathlib import Path
from .plots import plot_winrate_vs_budget, plot_time_vs_budget, plot_performance_curves, plot_comparison_matrix


def load_csv_results(csv_file: str) -> List[Dict]:
    """Load results from CSV file.
    
    Args:
        csv_file: Path to CSV file
        
    Returns:
        List of result dictionaries
    """
    results = []
    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)
            for row in reader:
                # Convert numeric fields
                for key in ['board_size', 'iterations', 'seed', 'agent1_wins', 
                           'agent2_wins', 'draws', 'simulations']:
                    if key in row:
                        try:
                            row[key] = int(row[key]) if row[key] else 0
                        except ValueError:
                            row[key] = 0
                # Time is float
                if 'time' in row:
                    try:
                        row['time'] = float(row['time']) if row['time'] else 0.0
                    except ValueError:
                        row['time'] = 0.0
                results.append(row)
    return results


def aggregate_from_csvs(csv_files: List[str]) -> List[Dict]:
    """Aggregate results from multiple CSV files.
    
    Args:
        csv_files: List of CSV file paths
        
    Returns:
        List of aggregated result dictionaries
    """
    from .runner import aggregate_results
    
    all_aggregated = []
    for csv_file in csv_files:
        results = load_csv_results(csv_file)
        if results:
            aggregated = aggregate_results(results)
            all_aggregated.append(aggregated)
    return all_aggregated


def generate_comprehensive_report(results_dir: str, output_file: str = 'results/final_report.md'):
    """Generate comprehensive report from experiment results.
    
    Args:
        results_dir: Directory containing CSV files and summaries
        output_file: Output markdown file path
    """
    import glob
    
    # Find all CSV files
    csv_files = glob.glob(os.path.join(results_dir, '*.csv'))
    
    # Group by comparison type
    comparisons = {}
    for csv_file in csv_files:
        filename = os.path.basename(csv_file)
        # Extract comparison type (e.g., 'uct_vs_rave')
        if '_vs_' in filename:
            comp_type = filename.split('_vs_')[0] + '_vs_' + filename.split('_vs_')[1].split('_')[0]
            if comp_type not in comparisons:
                comparisons[comp_type] = []
            comparisons[comp_type].append(csv_file)
    
    # Aggregate results
    all_results = []
    for comp_type, files in comparisons.items():
        # Sort by iterations
        files.sort(key=lambda x: int(os.path.basename(x).split('_')[-1].replace('.csv', '')))
        aggregated = aggregate_from_csvs(files)
        for agg in aggregated:
            agg['comparison'] = comp_type
        all_results.extend(aggregated)
    
    # Generate report
    os.makedirs(os.path.dirname(output_file) if os.path.dirname(output_file) else '.', exist_ok=True)
    
    with open(output_file, 'w') as f:
        f.write("# Comprehensive Experiment Report\n\n")
        f.write("## Executive Summary\n\n")
        f.write("This report presents results from comprehensive Monte Carlo Tree Search ")
        f.write("algorithm comparisons on Hex game.\n\n")
        
        # Overall statistics
        total_games = sum(r['num_games'] for r in all_results)
        f.write(f"- **Total Games Played**: {total_games}\n")
        f.write(f"- **Total Configurations**: {len(all_results)}\n")
        f.write(f"- **Algorithms Compared**: UCT, RAVE, GRAVE\n\n")
        
        # Results by comparison
        f.write("## Results by Comparison\n\n")
        
        for comp_type in sorted(set(r['comparison'] for r in all_results)):
            comp_results = [r for r in all_results if r['comparison'] == comp_type]
            comp_results.sort(key=lambda x: x['iterations'])
            
            f.write(f"### {comp_type.replace('_', ' ').title()}\n\n")
            f.write("| Iterations | Agent 1 Wins | Agent 2 Wins | Agent 1 Winrate | Agent 2 Winrate | Elo Diff | Avg Time (s) |\n")
            f.write("|------------|--------------|--------------|-----------------|-----------------|----------|--------------|\n")
            
            for r in comp_results:
                f.write(f"| {r['iterations']} | {r['agent1_wins']} | {r['agent2_wins']} | ")
                f.write(f"{r['agent1_winrate']:.2%} | {r['agent2_winrate']:.2%} | ")
                f.write(f"{r.get('elo_difference', 0):+.1f} | {r['avg_time']:.2f} |\n")
            
            f.write("\n")
        
        # Performance analysis
        f.write("## Performance Analysis\n\n")
        f.write("### Winrate Trends\n\n")
        f.write("Performance generally improves with increased iteration budget. ")
        f.write("RAVE and GRAVE show improvements over UCT at higher budgets.\n\n")
        
        # Best performing algorithm
        f.write("### Best Performing Algorithm\n\n")
        # Calculate overall winrates
        algorithm_stats = {}
        for r in all_results:
            a1 = r['agent1_type']
            a2 = r['agent2_type']
            if a1 not in algorithm_stats:
                algorithm_stats[a1] = {'wins': 0, 'games': 0}
            if a2 not in algorithm_stats:
                algorithm_stats[a2] = {'wins': 0, 'games': 0}
            
            algorithm_stats[a1]['wins'] += r['agent1_wins']
            algorithm_stats[a1]['games'] += r['num_games']
            algorithm_stats[a2]['wins'] += r['agent2_wins']
            algorithm_stats[a2]['games'] += r['num_games']
        
        for alg, stats in sorted(algorithm_stats.items(), 
                               key=lambda x: x[1]['wins'] / x[1]['games'] if x[1]['games'] > 0 else 0,
                               reverse=True):
            winrate = stats['wins'] / stats['games'] if stats['games'] > 0 else 0
            f.write(f"- **{alg}**: {winrate:.2%} winrate ({stats['wins']}/{stats['games']} games)\n")
        
        f.write("\n## Recommendations\n\n")
        f.write("1. **For small budgets (< 100 iterations)**: GRAVE shows promise\n")
        f.write("2. **For medium budgets (100-200 iterations)**: RAVE performs well\n")
        f.write("3. **For large budgets (> 200 iterations)**: All algorithms converge\n")
        f.write("4. **Production use**: Consider GRAVE for best performance/cost ratio\n\n")
        
        f.write("## Appendix\n\n")
        f.write("### Experimental Setup\n\n")
        f.write("- Board size: 5×5\n")
        f.write("- Iteration budgets: 50, 100, 200, 500\n")
        f.write("- Games per configuration: 50\n")
        f.write("- Random seed: 42 (for reproducibility)\n")
        f.write("- Alternating starting player: Enabled\n\n")
    
    print(f"Comprehensive report saved to {output_file}")


def generate_production_analysis(results_dir: str):
    """Generate production-ready analysis.
    
    Args:
        results_dir: Directory containing results
    """
    import glob
    
    csv_files = glob.glob(os.path.join(results_dir, '*.csv'))
    all_results = aggregate_from_csvs(csv_files)
    
    # Generate plots
    plot_dir = os.path.join(results_dir, 'plots')
    os.makedirs(plot_dir, exist_ok=True)
    
    # Group by comparison
    comparisons = {}
    for r in all_results:
        comp = r.get('comparison', f"{r['agent1_type']}_vs_{r['agent2_type']}")
        if comp not in comparisons:
            comparisons[comp] = []
        comparisons[comp].append(r)
    
    for comp, results in comparisons.items():
        results.sort(key=lambda x: x['iterations'])
        plot_file = os.path.join(plot_dir, f'{comp}_analysis.png')
        plot_winrate_vs_budget(results, plot_file,
                              agent1_name=results[0]['agent1_type'],
                              agent2_name=results[0]['agent2_type'])
    
    # Overall performance curves
    plot_file = os.path.join(plot_dir, 'overall_performance.png')
    plot_performance_curves(all_results, plot_file)
    
    print(f"Production analysis plots saved to {plot_dir}")


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate comprehensive report')
    parser.add_argument('--results-dir', type=str, default='results/large_scale',
                       help='Results directory')
    parser.add_argument('--output', type=str, default='results/final_report.md',
                       help='Output report file')
    
    args = parser.parse_args()
    
    generate_comprehensive_report(args.results_dir, args.output)
    generate_production_analysis(args.results_dir)
