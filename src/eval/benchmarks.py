"""Benchmarking scripts for comparing MCTS algorithms."""

import time
import random
from typing import Callable, Tuple, List, Dict, Optional
from ..games.hex import HexState, Player
from ..mcts.uct import UCTMCTS
from ..mcts.rave import RAVEMCTS
from ..mcts.grave import GRAVEMCTS
from .match import play_match


def create_agent(agent_type: str, iterations: int, random_seed: Optional[int] = None,
                 **kwargs) -> Callable:
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
        def agent(state: HexState) -> Tuple:
            return mcts.search(state, iterations)
        return agent
    elif agent_type == 'RAVE':
        mcts = RAVEMCTS(random_seed=random_seed)
        def agent(state: HexState) -> Tuple:
            return mcts.search(state, iterations)
        return agent
    elif agent_type == 'GRAVE':
        threshold = kwargs.get('threshold', 100)
        mcts = GRAVEMCTS(random_seed=random_seed, threshold=threshold)
        def agent(state: HexState) -> Tuple:
            return mcts.search(state, iterations)
        return agent
    else:
        raise ValueError(f"Unknown agent type: {agent_type}")


def run_benchmark(agent1_type: str, agent2_type: str, board_size: int,
                  iterations: int, num_games: int, seed: Optional[int] = None,
                  **kwargs) -> Dict:
    """Run benchmark between two agents.
    
    Args:
        agent1_type: Type of first agent ('UCT' or 'RAVE')
        agent2_type: Type of second agent ('UCT' or 'RAVE')
        board_size: Hex board size
        iterations: MCTS iterations per move
        num_games: Number of games to play
        seed: Random seed for reproducibility
        
    Returns:
        Dictionary with results: wins, losses, draws, times
    """
    agent1_wins = 0
    agent2_wins = 0
    draws = 0
    times = []
    
    for game_idx in range(num_games):
        game_seed = seed + game_idx if seed is not None else None
        random.seed(game_seed)
        
        # Create agents with different seeds to avoid identical play
        agent1 = create_agent(agent1_type, iterations, 
                             random_seed=game_seed, **kwargs)
        agent2 = create_agent(agent2_type, iterations,
                             random_seed=game_seed + 1000 if game_seed is not None else None,
                             **kwargs)
        
        initial_state = HexState(board_size)
        
        start_time = time.time()
        result = play_match(agent1, agent2, initial_state, verbose=False)
        elapsed = time.time() - start_time
        times.append(elapsed)
        
        if result == 1:
            agent1_wins += 1
        elif result == -1:
            agent2_wins += 1
        else:
            draws += 1
        
        if (game_idx + 1) % 10 == 0:
            print(f"Game {game_idx + 1}/{num_games} completed")
    
    return {
        'agent1_wins': agent1_wins,
        'agent2_wins': agent2_wins,
        'draws': draws,
        'agent1_winrate': agent1_wins / num_games,
        'agent2_winrate': agent2_wins / num_games,
        'avg_time': sum(times) / len(times),
        'total_time': sum(times)
    }


def compare_algorithms(board_size: int = 5, iterations_list: List[int] = [50, 100, 200],
                       num_games: int = 50, seed: int = 42, threshold: int = 100):
    """Compare UCT vs RAVE vs GRAVE at different iteration budgets.
    
    Args:
        board_size: Hex board size
        iterations_list: List of iteration budgets to test
        num_games: Number of games per configuration
        seed: Random seed
        threshold: GRAVE threshold T
    """
    print(f"Comparing UCT vs RAVE vs GRAVE on Hex {board_size}×{board_size}")
    print("=" * 70)
    
    results = []
    
    for iterations in iterations_list:
        print(f"\nIterations per move: {iterations}")
        print("-" * 70)
        
        # UCT vs RAVE
        print("UCT vs RAVE:")
        result_ur = run_benchmark('UCT', 'RAVE', board_size, iterations, num_games, seed)
        print(f"  UCT wins: {result_ur['agent1_wins']} ({result_ur['agent1_winrate']:.2%})")
        print(f"  RAVE wins: {result_ur['agent2_wins']} ({result_ur['agent2_winrate']:.2%})")
        
        # UCT vs GRAVE
        print("UCT vs GRAVE:")
        result_ug = run_benchmark('UCT', 'GRAVE', board_size, iterations, num_games, seed,
                                 threshold=threshold)
        print(f"  UCT wins: {result_ug['agent1_wins']} ({result_ug['agent1_winrate']:.2%})")
        print(f"  GRAVE wins: {result_ug['agent2_wins']} ({result_ug['agent2_winrate']:.2%})")
        
        # RAVE vs GRAVE
        print("RAVE vs GRAVE:")
        result_rg = run_benchmark('RAVE', 'GRAVE', board_size, iterations, num_games, seed,
                                 threshold=threshold)
        print(f"  RAVE wins: {result_rg['agent1_wins']} ({result_rg['agent1_winrate']:.2%})")
        print(f"  GRAVE wins: {result_rg['agent2_wins']} ({result_rg['agent2_winrate']:.2%})")
        
        results.append({
            'iterations': iterations,
            'uct_vs_rave': result_ur,
            'uct_vs_grave': result_ug,
            'rave_vs_grave': result_rg
        })
    
    return results


def compare_uct_vs_rave(board_size: int = 5, iterations_list: List[int] = [50, 100, 200],
                        num_games: int = 50, seed: int = 42):
    """Compare UCT vs RAVE at different iteration budgets.
    
    Args:
        board_size: Hex board size
        iterations_list: List of iteration budgets to test
        num_games: Number of games per configuration
        seed: Random seed
    """
    print(f"Comparing UCT vs RAVE on Hex {board_size}×{board_size}")
    print("=" * 60)
    
    results = []
    
    for iterations in iterations_list:
        print(f"\nIterations per move: {iterations}")
        print("-" * 60)
        
        # UCT vs RAVE
        result = run_benchmark('UCT', 'RAVE', board_size, iterations, num_games, seed)
        results.append({
            'iterations': iterations,
            'uct_wins': result['agent1_wins'],
            'rave_wins': result['agent2_wins'],
            'uct_winrate': result['agent1_winrate'],
            'rave_winrate': result['agent2_winrate'],
            'avg_time': result['avg_time']
        })
        
        print(f"UCT wins: {result['agent1_wins']} ({result['agent1_winrate']:.2%})")
        print(f"RAVE wins: {result['agent2_wins']} ({result['agent2_winrate']:.2%})")
        print(f"Draws: {result['draws']}")
        print(f"Avg time per game: {result['avg_time']:.2f}s")
    
    return results


if __name__ == '__main__':
    import sys
    from typing import Optional
    
    # Default parameters
    board_size = 5
    iterations_list = [50, 100, 200]
    num_games = 50
    seed = 42
    
    # Parse command line arguments if provided
    if len(sys.argv) > 1:
        board_size = int(sys.argv[1])
    if len(sys.argv) > 2:
        iterations_list = [int(x) for x in sys.argv[2].split(',')]
    if len(sys.argv) > 3:
        num_games = int(sys.argv[3])
    if len(sys.argv) > 4:
        seed = int(sys.argv[4])
    
    results = compare_uct_vs_rave(board_size, iterations_list, num_games, seed)
    
    # Print summary table
    print("\n" + "=" * 60)
    print("Summary Table")
    print("=" * 60)
    print(f"{'Iterations':<12} {'UCT Winrate':<15} {'RAVE Winrate':<15} {'Avg Time (s)':<15}")
    print("-" * 60)
    for r in results:
        print(f"{r['iterations']:<12} {r['uct_winrate']:<15.2%} {r['rave_winrate']:<15.2%} {r['avg_time']:<15.2f}")
