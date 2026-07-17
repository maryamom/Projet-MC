"""Unit tests for UCT MCTS implementation."""

import pytest
from src.games.hex import HexState, Player
from src.mcts.uct import UCTMCTS, MCTSNode


def test_mcts_node_creation():
    """Test MCTS node creation."""
    state = HexState(3)
    node = MCTSNode(state)
    assert node.N == 0
    assert node.W == 0.0
    assert len(node.children) == 0


def test_mcts_node_expansion():
    """Test node expansion."""
    state = HexState(3)
    node = MCTSNode(state)
    node.root_player = Player.BLACK
    
    child = node.expand()
    assert child is not None
    assert child.move in state.legal_moves()
    assert len(node.children) == 1


def test_uct_returns_legal_move():
    """Test UCT returns a legal move on tiny board."""
    state = HexState(3)
    mcts = UCTMCTS(random_seed=42)
    
    move = mcts.search(state, iterations=10)
    assert move is not None
    assert move in state.legal_moves()


def test_uct_deterministic():
    """Test UCT is deterministic with same seed."""
    state = HexState(3)
    mcts1 = UCTMCTS(random_seed=42)
    mcts2 = UCTMCTS(random_seed=42)
    
    move1 = mcts1.search(state, iterations=50)
    move2 = mcts2.search(state, iterations=50)
    
    assert move1 == move2


def test_backpropagation():
    """Test reward backpropagation."""
    state = HexState(3)
    root = MCTSNode(state)
    root.root_player = Player.BLACK
    
    child = root.expand()
    assert child is not None
    
    child.backpropagate(1.0)
    assert root.N == 1
    assert root.W == 1.0
    assert child.N == 1
    assert child.W == 1.0
