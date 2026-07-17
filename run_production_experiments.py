#!/usr/bin/env python3
"""Production experiment runner with comprehensive analysis."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.eval.batch_runner import run_batch_experiments
from src.eval.report_generator import generate_comprehensive_report, generate_production_analysis
from src.eval.analyzer import load_all_results, analyze_algorithm_performance, generate_statistical_summary
import argparse


def main():
    parser = argparse.ArgumentParser(description='Run production experiments with full analysis')
    parser.add_argument('--board-size', type=int, default=5,
                       help='Hex board size (default: 5)')
    parser.add_argument('--iterations', type=str, default='50,100,200,500',
                       help='Comma-separated iteration budgets')
    parser.add_argument('--games', type=int, default=50,
                       help='Games per configuration (default: 50)')
    parser.add_argument('--seed', type=int, default=42,
                       help='Random seed (default: 42)')
    parser.add_argument('--threshold', type=int, default=100,
                       help='GRAVE threshold (default: 100)')
    parser.add_argument('--output-dir', type=str, default='results/production',
                       help='Output directory (default: results/production)')
    parser.add_argument('--skip-experiments', action='store_true',
                       help='Skip running experiments (only generate reports)')
    
    args = parser.parse_args()
    
    iterations_list = [int(x.strip()) for x in args.iterations.split(',')]
    
    if not args.skip_experiments:
        print("=" * 80)
        print("RUNNING PRODUCTION EXPERIMENTS")
        print("=" * 80)
        print(f"Board size: {args.board_size}×{args.board_size}")
        print(f"Iterations: {iterations_list}")
        print(f"Games per configuration: {args.games}")
        print(f"Output directory: {args.output_dir}")
        print("=" * 80)
        
        run_batch_experiments(
            args.board_size, iterations_list, args.games,
            args.seed, args.threshold, args.output_dir
        )
    
    print("\n" + "=" * 80)
    print("GENERATING REPORTS AND ANALYSIS")
    print("=" * 80)
    
    # Generate comprehensive report
    report_file = os.path.join(args.output_dir, 'comprehensive_report.md')
    generate_comprehensive_report(args.output_dir, report_file)
    
    # Generate production analysis
    generate_production_analysis(args.output_dir)
    
    # Generate statistical analysis
    from src.eval.analyzer import analyze_algorithm_performance, analyze_budget_scaling
    results = load_all_results(args.output_dir)
    
    if results:
        performance = analyze_algorithm_performance(results)
        scaling = analyze_budget_scaling(results)
        
        analysis_file = os.path.join(args.output_dir, 'statistical_analysis.md')
        with open(analysis_file, 'w') as f:
            f.write("# Statistical Analysis\n\n")
            f.write("## Algorithm Performance Summary\n\n")
            f.write("| Algorithm | Winrate | Total Wins | Total Games | Avg Time (s) |\n")
            f.write("|-----------|---------|------------|-------------|--------------|\n")
            for algo, stats in sorted(performance.items(), key=lambda x: x[1]['winrate'], reverse=True):
                f.write(f"| {algo} | {stats['winrate']:.2%} | {stats['total_wins']} | ")
                f.write(f"{stats['total_games']} | {stats['avg_time']:.3f} |\n")
            
            f.write("\n## Budget Scaling\n\n")
            f.write("| Iterations | Configurations | Avg Winrate Spread | Avg Time (s) |\n")
            f.write("|------------|----------------|-------------------|--------------|\n")
            for iters, stats in sorted(scaling.items()):
                f.write(f"| {iters} | {stats['num_configurations']} | ")
                f.write(f"{stats['avg_winrate_spread']:.3f} | {stats['avg_time']:.3f} |\n")
        
        print(f"Statistical analysis saved to {analysis_file}")
    
    print("\n" + "=" * 80)
    print("PRODUCTION EXPERIMENTS COMPLETE")
    print("=" * 80)
    print(f"\nAll results saved to: {args.output_dir}")
    print(f"- Comprehensive report: {report_file}")
    print(f"- Statistical analysis: {analysis_file}")
    print(f"- Plots: {os.path.join(args.output_dir, 'plots')}")


if __name__ == '__main__':
    main()
