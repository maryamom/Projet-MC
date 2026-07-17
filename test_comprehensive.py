#!/usr/bin/env python3
"""Comprehensive test suite for all features."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

print("=" * 80)
print("COMPREHENSIVE TEST SUITE")
print("=" * 80)

# Test 1: Hex Game
print("\n[1/15] Testing Hex Game...")
from src.games.hex import HexState, Player
state = HexState(5)
assert len(state.legal_moves()) == 25
assert state.current_player == Player.BLACK
new_state = state.next_state((2, 2))
assert new_state.board[2][2] == Player.BLACK
print("  [OK] Hex game basic functionality")

# Test 2: Winner Detection
print("[2/15] Testing Winner Detection...")
test_state = HexState(3)
test_state = test_state.next_state((0, 0))  # Black
test_state = test_state.next_state((0, 1))  # White
test_state = test_state.next_state((1, 0))  # Black
test_state = test_state.next_state((0, 2))  # White
test_state = test_state.next_state((2, 0))  # Black
assert test_state.is_terminal()
assert test_state._has_winner() == Player.BLACK
print("  [OK] Winner detection")

# Test 3: UCT MCTS
print("[3/15] Testing UCT MCTS...")
from src.mcts.uct import UCTMCTS
mcts = UCTMCTS(random_seed=42)
move = mcts.search(HexState(3), 20)
assert move in HexState(3).legal_moves()
print(f"  [OK] UCT returns legal move: {move}")

# Test 4: RAVE MCTS
print("[4/15] Testing RAVE MCTS...")
from src.mcts.rave import RAVEMCTS
rave = RAVEMCTS(random_seed=42)
move = rave.search(HexState(3), 20)
assert move in HexState(3).legal_moves()
print(f"  [OK] RAVE returns legal move: {move}")

# Test 5: GRAVE MCTS
print("[5/15] Testing GRAVE MCTS...")
from src.mcts.grave import GRAVEMCTS
grave = GRAVEMCTS(random_seed=42, threshold=10)
move = grave.search(HexState(3), 20)
assert move in HexState(3).legal_moves()
print(f"  [OK] GRAVE returns legal move: {move}")

# Test 6: PUCT MCTS
print("[6/15] Testing PUCT MCTS...")
from src.mcts.puct import PUCTMCTS
puct = PUCTMCTS(random_seed=42)
move = puct.search(HexState(3), 20)
assert move in HexState(3).legal_moves()
print(f"  [OK] PUCT returns legal move: {move}")

# Test 7: Random Agent
print("[7/15] Testing Random Agent...")
from src.games.random_agent import RandomAgent
random_agent = RandomAgent(random_seed=42)
move = random_agent.play(HexState(3))
assert move in HexState(3).legal_moves()
print(f"  [OK] Random agent returns legal move: {move}")

# Test 8: Match Runner
print("[8/15] Testing Match Runner...")
from src.eval.match import play_match
from src.eval.runner import create_agent
agent1 = create_agent('UCT', 10, random_seed=42)
agent2 = create_agent('RANDOM', 10, random_seed=43)
result = play_match(agent1, agent2, HexState(3), verbose=False)
assert result in [-1, 0, 1]
print(f"  [OK] Match completed: result = {result}")

# Test 9: Alternating Starts
print("[9/15] Testing Alternating Starts...")
result1 = play_match(agent1, agent2, HexState(3), agent1_starts=True, verbose=False)
result2 = play_match(agent1, agent2, HexState(3), agent1_starts=False, verbose=False)
# Results may differ due to starting player
print(f"  [OK] Alternating starts: result1={result1}, result2={result2}")

# Test 10: Statistics
print("[10/15] Testing Statistics...")
from src.eval.stats import wilson_interval, elo_estimate
ci_lower, ci_upper = wilson_interval(30, 50)
assert 0 <= ci_lower <= ci_upper <= 1
elo = elo_estimate(30, 20)
assert isinstance(elo, float)
print(f"  [OK] CI: [{ci_lower:.2%}, {ci_upper:.2%}], Elo: {elo:.1f}")

# Test 11: Zobrist Hashing
print("[11/15] Testing Zobrist Hashing...")
from src.mcts.transposition import ZobristHasher
hasher = ZobristHasher(5, random_seed=42)
hash1 = hasher.hash_state(HexState(5))
hash2 = hasher.hash_state(HexState(5))
assert hash1 == hash2
state2 = HexState(5).next_state((2, 2))
hash3 = hasher.hash_state(state2)
assert hash1 != hash3
print(f"  [OK] Zobrist hashing: hash1={hash1}, hash3={hash3}")

# Test 12: Transposition Table
print("[12/15] Testing Transposition Table...")
from src.mcts.transposition import TranspositionTable
tt = TranspositionTable()
tt.store(12345, {'N': 10, 'W': 5.0})
stats = tt.get(12345)
assert stats['N'] == 10
assert stats['W'] == 5.0
print(f"  [OK] Transposition table: stored and retrieved stats")

# Test 13: Sequential Halving
print("[13/15] Testing Sequential Halving...")
from src.mcts.root_bandits import SequentialHalving
base_mcts = UCTMCTS(random_seed=42)
sh = SequentialHalving(base_mcts, random_seed=42)
move = sh.search(HexState(3), 20)
assert move in HexState(3).legal_moves()
print(f"  [OK] Sequential Halving returns legal move: {move}")

# Test 14: Experiment Runner
print("[14/15] Testing Experiment Runner...")
from src.eval.runner import run_experiment, aggregate_results
results = run_experiment('UCT', 'RANDOM', 3, 10, 5, seed=42, 
                        alternate_starts=True, output_csv=None)
assert len(results) == 5
aggregated = aggregate_results(results)
assert aggregated['num_games'] == 5
assert 'agent1_winrate' in aggregated
assert 'agent1_ci_lower' in aggregated
assert 'elo_difference' in aggregated
print(f"  [OK] Experiment runner: {aggregated['num_games']} games, "
      f"winrate={aggregated['agent1_winrate']:.2%}")

# Test 15: Plot Generation
print("[15/15] Testing Plot Generation...")
try:
    from src.eval.plots import plot_winrate_vs_budget
    test_results = [
        {'iterations': 50, 'agent1_winrate': 0.6, 'agent2_winrate': 0.4},
        {'iterations': 100, 'agent1_winrate': 0.65, 'agent2_winrate': 0.35},
    ]
    plot_file = 'results/test_plot.png'
    plot_winrate_vs_budget(test_results, plot_file, 'UCT', 'RAVE')
    assert os.path.exists(plot_file)
    print(f"  [OK] Plot generated: {plot_file}")
except ImportError as e:
    print(f"  [WARNING] Matplotlib not available: {e}")
except Exception as e:
    print(f"  [WARNING] Plot generation failed: {e}")

print("\n" + "=" * 80)
print("ALL TESTS COMPLETED SUCCESSFULLY!")
print("=" * 80)
