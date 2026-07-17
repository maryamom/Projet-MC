"""CLI experiment runner for MCTS algorithms."""

import argparse
import csv
import time
import os
from typing import List, Dict, Optional
from pathlib import Path
from ..games.hex import HexState
from ..games.random_agent import create_random_agent
from ..mcts.uct import UCTMCTS
from ..mcts.rave import RAVEMCTS
from ..mcts.grave import GRAVEMCTS
from ..mcts.puct import PUCTMCTS
from .match import play_match
from .stats import wilson_interval, elo_estimate


def create_agent(agent_type: str, iterations: int, random_seed: Optional[int] = None,
                 **kwargs):
    """Create an agent function.
    
    Args:
        agent_type: 'UCT', 'RAVE', or 'GRAVE'
        iterations: Number of MCTS iterations per move
        random_seed: Random seed for reproducibility
        **kwargs: Additional arguments (e.g., threshold for GRAVE)
        
    Returns:
        Agent function taking state and returning move
    """
    if agent_type == 'UCT':
        mcts = UCTMCTS(random_seed=random_seed)
        def agent(state: HexState):
            return mcts.search(state, iterations)
        return agent
    elif agent_type == 'RAVE':
        mcts = RAVEMCTS(random_seed=random_seed)
        def agent(state: HexState):
            return mcts.search(state, iterations)
        return agent
    elif agent_type == 'GRAVE':
        threshold = kwargs.get('threshold', 100)
        mcts = GRAVEMCTS(random_seed=random_seed, threshold=threshold)
        def agent(state: HexState):
            return mcts.search(state, iterations)
        return agent
    elif agent_type == 'PUCT':
        c_puct = kwargs.get('c_puct', 1.0)
        use_value_bootstrap = kwargs.get('use_value_bootstrap', True)
        mcts = PUCTMCTS(random_seed=random_seed, c_puct=c_puct,
                       use_value_bootstrap=use_value_bootstrap)
        def agent(state: HexState):
            return mcts.search(state, iterations)
        return agent
    elif agent_type == 'RANDOM':
        return create_random_agent(random_seed=random_seed)
    else:
        raise ValueError(f"Unknown agent type: {agent_type}")


def run_match(agent1_type: str, agent2_type: str, board_size: int,
              iterations: int, seed: Optional[int] = None, 
              agent1_starts: bool = True, **kwargs) -> Dict:
    """Run a single match between two agents.
    
    Args:
        agent1_type: Type of first agent
        agent2_type: Type of second agent
        board_size: Hex board size
        iterations: MCTS iterations per move
        seed: Random seed
        agent1_starts: If True, agent1 plays as BLACK (first)
        **kwargs: Additional agent parameters
        
    Returns:
        Dictionary with match results including simulation counts
    """
    import random
    random.seed(seed)
    
    agent1 = create_agent(agent1_type, iterations, 
                         random_seed=seed, **kwargs)
    agent2 = create_agent(agent2_type, iterations,
                         random_seed=seed + 1000 if seed is not None else None,
                         **kwargs)
    
    initial_state = HexState(board_size)
    
    # Track simulations (approximate: iterations * number of moves)
    simulations = 0
    
    start_time = time.time()
    result = play_match(agent1, agent2, initial_state, verbose=False, 
                       agent1_starts=agent1_starts)
    elapsed = time.time() - start_time
    
    # Estimate simulations: iterations per move * average game length
    # For Hex 5x5, average game length is roughly board_size^2 / 2
    avg_game_length = (board_size * board_size) // 2
    simulations = iterations * avg_game_length * 2  # Both players
    
    return {
        'agent1_type': agent1_type,
        'agent2_type': agent2_type,
        'board_size': board_size,
        'iterations': iterations,
        'seed': seed,
        'agent1_starts': agent1_starts,
        'result': result,
        'agent1_wins': 1 if result == 1 else 0,
        'agent2_wins': 1 if result == -1 else 0,
        'draws': 1 if result == 0 else 0,
        'time': elapsed,
        'simulations': simulations
    }


def run_experiment(agent1_type: str, agent2_type: str, board_size: int,
                  iterations: int, num_games: int, seed: int = 42,
                  output_csv: Optional[str] = None, alternate_starts: bool = True,
                  **kwargs) -> List[Dict]:
    """Run an experiment with multiple games.
    
    Args:
        agent1_type: Type of first agent
        agent2_type: Type of second agent
        board_size: Hex board size
        iterations: MCTS iterations per move
        num_games: Number of games to play
        seed: Random seed
        output_csv: Optional CSV file path to save results
        alternate_starts: If True, alternate which agent starts (agent1 starts in half)
        **kwargs: Additional agent parameters
        
    Returns:
        List of match result dictionaries
    """
    results = []
    
    print(f"Running experiment: {agent1_type} vs {agent2_type}")
    print(f"Board size: {board_size}×{board_size}, Iterations: {iterations}, Games: {num_games}")
    if alternate_starts:
        print("Alternating starting player: enabled")
    print("-" * 70)
    
    for game_idx in range(num_games):
        game_seed = seed + game_idx
        # Alternate starting player if requested
        agent1_starts = True if not alternate_starts else (game_idx % 2 == 0)
        result = run_match(agent1_type, agent2_type, board_size, iterations,
                          seed=game_seed, agent1_starts=agent1_starts, **kwargs)
        results.append(result)
        
        if (game_idx + 1) % 10 == 0:
            agent1_wins = sum(r['agent1_wins'] for r in results)
            agent2_wins = sum(r['agent2_wins'] for r in results)
            draws = sum(r['draws'] for r in results)
            print(f"Game {game_idx + 1}/{num_games}: "
                  f"{agent1_type} {agent1_wins} - {agent2_wins} {agent2_type} "
                  f"(draws: {draws})")
    
    # Save to CSV if requested
    if output_csv:
        save_results_csv(results, output_csv)
    
    return results


def save_results_csv(results: List[Dict], filename: str):
    """Save results to CSV file.
    
    Args:
        results: List of result dictionaries
        filename: Output CSV file path
    """
    if not results:
        return
    
    fieldnames = list(results[0].keys())
    
    # Create directory if needed
    os.makedirs(os.path.dirname(filename) if os.path.dirname(filename) else '.', exist_ok=True)
    
    with open(filename, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)


def aggregate_results(results: List[Dict]) -> Dict:
    """Aggregate results from multiple matches.
    
    Args:
        results: List of match result dictionaries
        
    Returns:
        Aggregated statistics with confidence intervals
    """
    if not results:
        return {}
    
    agent1_type = results[0]['agent1_type']
    agent2_type = results[0]['agent2_type']
    
    agent1_wins = sum(r['agent1_wins'] for r in results)
    agent2_wins = sum(r['agent2_wins'] for r in results)
    draws = sum(r['draws'] for r in results)
    total_time = sum(r['time'] for r in results)
    total_simulations = sum(r.get('simulations', 0) for r in results)
    avg_time = total_time / len(results)
    avg_simulations = total_simulations / len(results) if results else 0
    
    num_games = len(results)
    agent1_winrate = agent1_wins / num_games
    agent2_winrate = agent2_wins / num_games
    
    # Calculate confidence intervals
    ci1_lower, ci1_upper = wilson_interval(agent1_wins, num_games)
    ci2_lower, ci2_upper = wilson_interval(agent2_wins, num_games)
    
    # Calculate Elo difference
    elo_diff = elo_estimate(agent1_wins, agent2_wins, draws)
    
    return {
        'agent1_type': agent1_type,
        'agent2_type': agent2_type,
        'board_size': results[0]['board_size'],
        'iterations': results[0]['iterations'],
        'num_games': num_games,
        'agent1_wins': agent1_wins,
        'agent2_wins': agent2_wins,
        'draws': draws,
        'agent1_winrate': agent1_winrate,
        'agent2_winrate': agent2_winrate,
        'agent1_ci_lower': ci1_lower,
        'agent1_ci_upper': ci1_upper,
        'agent2_ci_lower': ci2_lower,
        'agent2_ci_upper': ci2_upper,
        'elo_difference': elo_diff,
        'total_time': total_time,
        'avg_time': avg_time,
        'total_simulations': total_simulations,
        'avg_simulations': avg_simulations
    }


def generate_summary_markdown(all_results: List[Dict], output_file: str):
    """Generate markdown summary table from aggregated results.
    
    Args:
        all_results: List of aggregated result dictionaries
        output_file: Output markdown file path
    """
    # Create results directory if needed
    os.makedirs(os.path.dirname(output_file) if os.path.dirname(output_file) else '.', exist_ok=True)
    
    with open(output_file, 'w') as f:
        f.write("# Experiment Results Summary\n\n")
        f.write("## Comparison Table\n\n")
        f.write("| Agent 1 | Agent 2 | Board Size | Iterations | Games | ")
        f.write("Agent 1 Wins | Agent 2 Wins | Draws | Agent 1 Winrate (95% CI) | Agent 2 Winrate (95% CI) | Elo Diff | Avg Time (s) | Avg Sims |\n")
        f.write("|---------|---------|------------|------------|-------|")
        f.write("-------------|--------------|-------|------------------------|------------------------|----------|--------------|----------|\n")
        
        for result in all_results:
            ci1_str = f"[{result.get('agent1_ci_lower', 0):.2%}, {result.get('agent1_ci_upper', 1):.2%}]"
            ci2_str = f"[{result.get('agent2_ci_lower', 0):.2%}, {result.get('agent2_ci_upper', 1):.2%}]"
            f.write(f"| {result['agent1_type']} | {result['agent2_type']} | ")
            f.write(f"{result['board_size']}×{result['board_size']} | ")
            f.write(f"{result['iterations']} | {result['num_games']} | ")
            f.write(f"{result['agent1_wins']} | {result['agent2_wins']} | ")
            f.write(f"{result['draws']} | {result['agent1_winrate']:.2%} {ci1_str} | ")
            f.write(f"{result['agent2_winrate']:.2%} {ci2_str} | ")
            f.write(f"{result.get('elo_difference', 0):+.1f} | ")
            f.write(f"{result['avg_time']:.2f} | ")
            f.write(f"{result.get('avg_simulations', 0):.0f} |\n")
        
        f.write("\n## Notes\n\n")
        f.write("- Winrate is calculated as wins / total games\n")
        f.write("- 95% CI: Wilson confidence interval\n")
        f.write("- Elo Diff: Estimated Elo difference (positive = Agent 1 stronger)\n")
        f.write("- Time is average time per game\n")
        f.write("- Sims is average simulations per game\n")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description='Run MCTS experiments')
    parser.add_argument('--agent1', type=str, default='UCT',
                       choices=['UCT', 'RAVE', 'GRAVE', 'PUCT', 'RANDOM'],
                       help='First agent type')
    parser.add_argument('--agent2', type=str, default='RAVE',
                       choices=['UCT', 'RAVE', 'GRAVE', 'PUCT', 'RANDOM'],
                       help='Second agent type')
    parser.add_argument('--board-size', type=int, default=5,
                       help='Hex board size (default: 5)')
    parser.add_argument('--iterations', type=int, default=100,
                       help='MCTS iterations per move (default: 100)')
    parser.add_argument('--games', type=int, default=50,
                       help='Number of games to play (default: 50)')
    parser.add_argument('--seed', type=int, default=42,
                       help='Random seed (default: 42)')
    parser.add_argument('--threshold', type=int, default=100,
                       help='GRAVE threshold T (default: 100)')
    parser.add_argument('--c-puct', type=float, default=1.0,
                       help='PUCT exploration constant (default: 1.0)')
    parser.add_argument('--output-csv', type=str, default=None,
                       help='Output CSV file path')
    parser.add_argument('--output-md', type=str, default='results/summary.md',
                       help='Output markdown summary file (default: results/summary.md)')
    parser.add_argument('--no-alternate-starts', action='store_true',
                       help='Disable alternating starting player')
    
    args = parser.parse_args()
    
    kwargs = {}
    if args.agent1 == 'GRAVE' or args.agent2 == 'GRAVE':
        kwargs['threshold'] = args.threshold
    if args.agent1 == 'PUCT' or args.agent2 == 'PUCT':
        kwargs['c_puct'] = args.c_puct
    
    results = run_experiment(
        args.agent1, args.agent2, args.board_size,
        args.iterations, args.games, args.seed,
        output_csv=args.output_csv, 
        alternate_starts=not args.no_alternate_starts,
        **kwargs
    )
    
    aggregated = aggregate_results(results)
    
    print("\n" + "=" * 70)
    print("Final Results:")
    print("=" * 70)
    print(f"{aggregated['agent1_type']} wins: {aggregated['agent1_wins']} "
          f"({aggregated['agent1_winrate']:.2%})")
    print(f"{aggregated['agent2_type']} wins: {aggregated['agent2_wins']} "
          f"({aggregated['agent2_winrate']:.2%})")
    print(f"Draws: {aggregated['draws']}")
    print(f"\nConfidence Intervals (95%):")
    print(f"  {aggregated['agent1_type']}: [{aggregated.get('agent1_ci_lower', 0):.2%}, "
          f"{aggregated.get('agent1_ci_upper', 1):.2%}]")
    print(f"  {aggregated['agent2_type']}: [{aggregated.get('agent2_ci_lower', 0):.2%}, "
          f"{aggregated.get('agent2_ci_upper', 1):.2%}]")
    print(f"\nElo Difference: {aggregated.get('elo_difference', 0):+.1f} "
          f"(positive = {aggregated['agent1_type']} stronger)")
    print(f"Average time per game: {aggregated['avg_time']:.2f}s")
    print(f"Average simulations per game: {aggregated.get('avg_simulations', 0):.0f}")
    
    # Generate summary markdown
    generate_summary_markdown([aggregated], args.output_md)
    print(f"\nSummary saved to {args.output_md}")


if __name__ == '__main__':
    main()
