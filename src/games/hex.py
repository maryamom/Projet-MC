"""Hex game implementation.

This module provides a clean interface for the Hex game that can be used
with MCTS algorithms. The game state is immutable to ensure safe tree search.
"""

from typing import List, Tuple, Optional, Set
from enum import IntEnum


class Player(IntEnum):
    """Player enumeration."""
    EMPTY = 0
    BLACK = 1
    WHITE = 2


class HexState:
    """Immutable Hex game state."""
    
    def __init__(self, size: int, board: Optional[List[List[int]]] = None, 
                 current_player: int = Player.BLACK):
        """Initialize Hex game state.
        
        Args:
            size: Board size (N×N)
            board: Optional board state (defaults to empty board)
            current_player: Player to move (BLACK or WHITE)
        """
        self.size = size
        if board is None:
            self.board = [[Player.EMPTY for _ in range(size)] for _ in range(size)]
        else:
            # Deep copy for immutability
            self.board = [row[:] for row in board]
        self.current_player = current_player
    
    def legal_moves(self) -> List[Tuple[int, int]]:
        """Return list of legal moves as (row, col) tuples."""
        moves = []
        for r in range(self.size):
            for c in range(self.size):
                if self.board[r][c] == Player.EMPTY:
                    moves.append((r, c))
        return moves
    
    def next_state(self, move: Tuple[int, int]) -> 'HexState':
        """Return new state after applying move.
        
        Args:
            move: (row, col) tuple
            
        Returns:
            New HexState with move applied
        """
        r, c = move
        new_board = [row[:] for row in self.board]
        new_board[r][c] = self.current_player
        next_player = Player.WHITE if self.current_player == Player.BLACK else Player.BLACK
        return HexState(self.size, new_board, next_player)
    
    def is_terminal(self) -> bool:
        """Check if game is over."""
        return self._has_winner() is not None
    
    def _has_winner(self) -> Optional[int]:
        """Check for winner using BFS.
        
        Returns:
            Player.BLACK, Player.WHITE, or None if no winner
        """
        # Check Black (top to bottom)
        if self._check_connection(Player.BLACK, 0, self.size - 1):
            return Player.BLACK
        
        # Check White (left to right)
        if self._check_connection(Player.WHITE, 0, self.size - 1, is_white=True):
            return Player.WHITE
        
        return None
    
    def _check_connection(self, player: int, start_row: int, end_row: int, 
                         is_white: bool = False) -> bool:
        """Check if player has connected their sides using BFS."""
        visited = set()
        queue = []
        
        # Initialize queue with starting positions
        if is_white:
            # White: start from left column (col 0)
            for r in range(self.size):
                if self.board[r][0] == player:
                    queue.append((r, 0))
                    visited.add((r, 0))
            target_col = self.size - 1
        else:
            # Black: start from top row (row 0)
            for c in range(self.size):
                if self.board[0][c] == player:
                    queue.append((0, c))
                    visited.add((0, c))
            target_col = None
        
        # Hex neighbors: 6 directions
        neighbors = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, 1), (1, -1)]
        
        while queue:
            r, c = queue.pop(0)
            
            # Check if reached target side
            if is_white and c == target_col:
                return True
            elif not is_white and r == end_row:
                return True
            
            # Explore neighbors
            for dr, dc in neighbors:
                nr, nc = r + dr, c + dc
                if (0 <= nr < self.size and 0 <= nc < self.size and
                    (nr, nc) not in visited and
                    self.board[nr][nc] == player):
                    queue.append((nr, nc))
                    visited.add((nr, nc))
        
        return False
    
    def reward(self, root_player: int) -> float:
        """Return reward from root_player's perspective.
        
        Args:
            root_player: Player.BLACK or Player.WHITE
            
        Returns:
            1.0 if root_player wins, -1.0 if loses, 0.0 if draw/ongoing
        """
        winner = self._has_winner()
        if winner is None:
            return 0.0
        return 1.0 if winner == root_player else -1.0
    
    def serialize(self) -> Tuple:
        """Serialize state for hashing.
        
        Returns:
            Tuple representation suitable for hashing
        """
        board_tuple = tuple(tuple(row) for row in self.board)
        return (board_tuple, self.current_player)
    
    def __hash__(self) -> int:
        """Hash state for use in sets/dicts."""
        return hash(self.serialize())
    
    def __eq__(self, other) -> bool:
        """Check equality."""
        if not isinstance(other, HexState):
            return False
        return (self.size == other.size and
                self.board == other.board and
                self.current_player == other.current_player)
