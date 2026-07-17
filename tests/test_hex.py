"""Unit tests for Hex game implementation."""

import pytest
from src.games.hex import HexState, Player


def test_initial_state():
    """Test initial state creation."""
    state = HexState(5)
    assert state.size == 5
    assert state.current_player == Player.BLACK
    assert len(state.legal_moves()) == 25


def test_legal_moves():
    """Test legal moves generation."""
    state = HexState(3)
    moves = state.legal_moves()
    assert len(moves) == 9
    assert (0, 0) in moves
    assert (2, 2) in moves


def test_move_application():
    """Test applying moves."""
    state = HexState(3)
    new_state = state.next_state((1, 1))
    
    assert new_state.board[1][1] == Player.BLACK
    assert new_state.current_player == Player.WHITE
    assert state.board[1][1] == Player.EMPTY  # Original unchanged


def test_winner_detection_black():
    """Test Black winner detection (top to bottom)."""
    state = HexState(3)
    # Create a winning path for Black
    moves = [(0, 0), (1, 0), (2, 0)]  # Vertical line
    for move in moves:
        state = state.next_state(move)
    
    assert state.is_terminal()
    assert state._has_winner() == Player.BLACK


def test_winner_detection_white():
    """Test White winner detection (left to right)."""
    state = HexState(3)
    # Create a winning path for White
    moves = [(0, 0), (0, 1), (0, 2)]  # Horizontal line
    for move in moves:
        state = state.next_state(move)
    
    assert state.is_terminal()
    assert state._has_winner() == Player.WHITE


def test_legal_move_count():
    """Test legal move count decreases as game progresses."""
    state = HexState(5)
    initial_count = len(state.legal_moves())
    
    state = state.next_state((2, 2))
    assert len(state.legal_moves()) == initial_count - 1
    
    state = state.next_state((1, 1))
    assert len(state.legal_moves()) == initial_count - 2


def test_serialization():
    """Test state serialization for hashing."""
    state1 = HexState(3)
    state2 = HexState(3)
    
    assert hash(state1) == hash(state2)
    
    state1 = state1.next_state((1, 1))
    assert hash(state1) != hash(state2)


def test_reward():
    """Test reward calculation."""
    state = HexState(3)
    # Create winning state for Black
    moves = [(0, 0), (1, 0), (2, 0)]
    for move in moves:
        state = state.next_state(move)
    
    assert state.reward(Player.BLACK) == 1.0
    assert state.reward(Player.WHITE) == -1.0
