"""Plotting and visualization utilities for experiment results."""

import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import numpy as np
from typing import List, Dict, Optional
import os


def plot_winrate_vs_budget(results: List[Dict], output_file: str, 
                           agent1_name: str = "Agent 1", 
                           agent2_name: str = "Agent 2"):
    """Plot winrate vs iteration budget.
    
    Args:
        results: List of result dictionaries with 'iterations' and winrate keys
        output_file: Output file path for the plot
        agent1_name: Name for agent 1
        agent2_name: Name for agent 2
    """
    iterations = [r['iterations'] for r in results]
    agent1_winrates = [r.get('agent1_winrate', 0) for r in results]
    agent2_winrates = [r.get('agent2_winrate', 0) for r in results]
    
    plt.figure(figsize=(10, 6))
    plt.plot(iterations, agent1_winrates, 'o-', label=agent1_name, linewidth=2, markersize=8)
    plt.plot(iterations, agent2_winrates, 's-', label=agent2_name, linewidth=2, markersize=8)
    plt.axhline(y=0.5, color='gray', linestyle='--', alpha=0.5, label='Equal')
    plt.xlabel('Iterations per Move', fontsize=12)
    plt.ylabel('Winrate', fontsize=12)
    plt.title(f'Winrate vs Iteration Budget: {agent1_name} vs {agent2_name}', fontsize=14)
    plt.legend(loc='best', fontsize=10)
    plt.grid(True, alpha=0.3)
    plt.ylim([0, 1])
    plt.tight_layout()
    
    os.makedirs(os.path.dirname(output_file) if os.path.dirname(output_file) else '.', exist_ok=True)
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Plot saved to {output_file}")


def plot_time_vs_budget(results: List[Dict], output_file: str):
    """Plot average time vs iteration budget.
    
    Args:
        results: List of result dictionaries with 'iterations' and 'avg_time' keys
        output_file: Output file path for the plot
    """
    iterations = [r['iterations'] for r in results]
    avg_times = [r.get('avg_time', 0) for r in results]
    
    plt.figure(figsize=(10, 6))
    plt.plot(iterations, avg_times, 'o-', color='green', linewidth=2, markersize=8)
    plt.xlabel('Iterations per Move', fontsize=12)
    plt.ylabel('Average Time per Game (seconds)', fontsize=12)
    plt.title('Average Time vs Iteration Budget', fontsize=14)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    
    os.makedirs(os.path.dirname(output_file) if os.path.dirname(output_file) else '.', exist_ok=True)
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Plot saved to {output_file}")


def plot_comparison_matrix(all_results: List[Dict], output_file: str):
    """Plot comparison matrix showing all algorithm pairs.
    
    Args:
        all_results: List of aggregated result dictionaries
        output_file: Output file path for the plot
    """
    # Extract unique algorithms and budgets
    algorithms = set()
    iterations_set = set()
    for r in all_results:
        algorithms.add(r['agent1_type'])
        algorithms.add(r['agent2_type'])
        iterations_set.add(r['iterations'])
    
    algorithms = sorted(list(algorithms))
    iterations = sorted(list(iterations_set))
    
    # Create comparison matrix
    fig, axes = plt.subplots(len(iterations), 1, figsize=(10, 4 * len(iterations)))
    if len(iterations) == 1:
        axes = [axes]
    
    for idx, iters in enumerate(iterations):
        ax = axes[idx]
        # Filter results for this iteration budget
        relevant = [r for r in all_results if r['iterations'] == iters]
        
        # Create winrate matrix
        winrates = {}
        for r in relevant:
            key = (r['agent1_type'], r['agent2_type'])
            winrates[key] = r['agent1_winrate']
        
        # Plot bars
        comparisons = []
        values = []
        labels = []
        for a1 in algorithms:
            for a2 in algorithms:
                if a1 != a2:
                    key = (a1, a2)
                    if key in winrates:
                        comparisons.append(f"{a1} vs {a2}")
                        values.append(winrates[key])
                        labels.append(f"{a1} wins")
        
        if values:
            bars = ax.barh(comparisons, values, alpha=0.7)
            ax.axvline(x=0.5, color='red', linestyle='--', alpha=0.5)
            ax.set_xlabel('Winrate', fontsize=10)
            ax.set_title(f'Iterations: {iters}', fontsize=12)
            ax.set_xlim([0, 1])
            ax.grid(True, alpha=0.3, axis='x')
            
            # Add value labels
            for i, (bar, val) in enumerate(zip(bars, values)):
                ax.text(val + 0.02, i, f'{val:.2%}', va='center', fontsize=9)
    
    plt.tight_layout()
    os.makedirs(os.path.dirname(output_file) if os.path.dirname(output_file) else '.', exist_ok=True)
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Comparison matrix saved to {output_file}")


def plot_performance_curves(all_results: List[Dict], output_file: str):
    """Plot performance curves for all algorithms.
    
    Args:
        all_results: List of aggregated result dictionaries
        output_file: Output file path for the plot
    """
    # Group by algorithm pairs
    pairs = {}
    for r in all_results:
        pair_key = (r['agent1_type'], r['agent2_type'])
        if pair_key not in pairs:
            pairs[pair_key] = []
        pairs[pair_key].append(r)
    
    # Sort each pair by iterations
    for key in pairs:
        pairs[key].sort(key=lambda x: x['iterations'])
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    
    # Plot 1: Winrate curves
    for (a1, a2), results in pairs.items():
        iterations = [r['iterations'] for r in results]
        winrates = [r['agent1_winrate'] for r in results]
        ax1.plot(iterations, winrates, 'o-', label=f'{a1} vs {a2}', linewidth=2, markersize=6)
    
    ax1.axhline(y=0.5, color='gray', linestyle='--', alpha=0.5)
    ax1.set_xlabel('Iterations per Move', fontsize=12)
    ax1.set_ylabel('Winrate (Agent 1)', fontsize=12)
    ax1.set_title('Winrate vs Iteration Budget', fontsize=14)
    ax1.legend(loc='best', fontsize=9)
    ax1.grid(True, alpha=0.3)
    ax1.set_ylim([0, 1])
    
    # Plot 2: Time curves
    for (a1, a2), results in pairs.items():
        iterations = [r['iterations'] for r in results]
        times = [r['avg_time'] for r in results]
        ax2.plot(iterations, times, 's-', label=f'{a1} vs {a2}', linewidth=2, markersize=6)
    
    ax2.set_xlabel('Iterations per Move', fontsize=12)
    ax2.set_ylabel('Average Time per Game (seconds)', fontsize=12)
    ax2.set_title('Time vs Iteration Budget', fontsize=14)
    ax2.legend(loc='best', fontsize=9)
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    os.makedirs(os.path.dirname(output_file) if os.path.dirname(output_file) else '.', exist_ok=True)
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Performance curves saved to {output_file}")
