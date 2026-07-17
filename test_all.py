#!/usr/bin/env python3
"""Quick test script to verify all components work."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.games.hex import HexState, Player
from src.mcts.uct import UCTMCTS, MCTSNode
from src.mcts.rave import RAVEMCTS
from src.mcts.grave import GRAVEMCTS
from src.eval.match import play_match

print("=" * 70)
print("Testing Hex Game")
print("=" * 70)

# Test 1: Initial state
state = HexState(5)
assert state.size == 5
assert state.current_player == Player.BLACK
assert len(state.legal_moves()) == 25
print("[OK] Initial state test passed")

# Test 2: Move application
new_state = state.next_state((2, 2))
assert new_state.board[2][2] == Player.BLACK
assert new_state.current_player == Player.WHITE
assert state.board[2][2] == Player.EMPTY  # Original unchanged
print("[OK] Move application test passed")

# Test 3: Winner detection (Black)
test_state = HexState(3)
# Black plays vertical line: (0,0), (1,0), (2,0)
# Need to skip White's turns by playing dummy moves
test_state = test_state.next_state((0, 0))  # Black
test_state = test_state.next_state((0, 1))  # White (dummy)
test_state = test_state.next_state((1, 0))  # Black
test_state = test_state.next_state((0, 2))  # White (dummy)
test_state = test_state.next_state((2, 0))  # Black
assert test_state.is_terminal()
assert test_state._has_winner() == Player.BLACK
print("[OK] Black winner detection test passed")

# Test 4: Winner detection (White)
test_state = HexState(3)
# White plays horizontal line: (0,0), (0,1), (0,2)
# Need to skip Black's turns by playing dummy moves
test_state = test_state.next_state((1, 1))  # Black (dummy)
test_state = test_state.next_state((0, 0))  # White
test_state = test_state.next_state((2, 2))  # Black (dummy)
test_state = test_state.next_state((0, 1))  # White
test_state = test_state.next_state((1, 2))  # Black (dummy)
test_state = test_state.next_state((0, 2))  # White
assert test_state.is_terminal()
assert test_state._has_winner() == Player.WHITE
print("[OK] White winner detection test passed")

print("\n" + "=" * 70)
print("Testing UCT MCTS")
print("=" * 70)

# Test 5: UCT returns legal move
state = HexState(3)
mcts = UCTMCTS(random_seed=42)
move = mcts.search(state, iterations=10)
assert move is not None
assert move in state.legal_moves()
print(f"[OK] UCT returns legal move: {move}")

# Test 6: UCT deterministic (with more iterations)
import random
random.seed(42)
mcts1 = UCTMCTS(random_seed=42)
move1 = mcts1.search(state, iterations=100)
random.seed(42)
mcts2 = UCTMCTS(random_seed=42)
move2 = mcts2.search(state, iterations=100)
assert move1 == move2, f"Moves differ: {move1} != {move2}"
print(f"[OK] UCT deterministic: {move1} == {move2}")

print("\n" + "=" * 70)
print("Testing RAVE MCTS")
print("=" * 70)

# Test 7: RAVE returns legal move
state = HexState(3)
rave = RAVEMCTS(random_seed=42)
move = rave.search(state, iterations=10)
assert move is not None
assert move in state.legal_moves()
print(f"[OK] RAVE returns legal move: {move}")

print("\n" + "=" * 70)
print("Testing GRAVE MCTS")
print("=" * 70)

# Test 8: GRAVE returns legal move
state = HexState(3)
grave = GRAVEMCTS(random_seed=42, threshold=10)
move = grave.search(state, iterations=10)
assert move is not None
assert move in state.legal_moves()
print(f"[OK] GRAVE returns legal move: {move}")

print("\n" + "=" * 70)
print("Testing Match Runner")
print("=" * 70)

# Test 9: Match runner
def create_agent(agent_type, iterations, seed):
    if agent_type == 'UCT':
        mcts = UCTMCTS(random_seed=seed)
        return lambda s: mcts.search(s, iterations)
    elif agent_type == 'RAVE':
        mcts = RAVEMCTS(random_seed=seed)
        return lambda s: mcts.search(s, iterations)
    else:
        raise ValueError(f"Unknown: {agent_type}")

agent1 = create_agent('UCT', 20, 42)
agent2 = create_agent('RAVE', 20, 43)
initial_state = HexState(3)
result = play_match(agent1, agent2, initial_state, verbose=False)
assert result in [-1, 0, 1]
print(f"[OK] Match completed: result = {result}")

print("\n" + "=" * 70)
print("ALL TESTS PASSED! [OK]")
print("=" * 70)
