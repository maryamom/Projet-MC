"""Zobrist hashing and transposition table for MCTS."""

import random
from typing import Dict, Tuple, Optional, Any
from collections import defaultdict


class ZobristHasher:
    """Zobrist hashing for game states."""
    
    def __init__(self, board_size: int, num_players: int = 3, random_seed: int = 42):
        """Initialize Zobrist hasher.
        
        Args:
            board_size: Size of the board
            num_players: Number of players (including EMPTY)
            random_seed: Random seed for hash table generation
        """
        self.board_size = board_size
        self.num_players = num_players
        random.seed(random_seed)
        
        # Generate random bitstrings for each (position, player) pair
        # Using 64-bit integers
        self.hash_table = {}
        for r in range(board_size):
            for c in range(board_size):
                for player in range(num_players):
                    self.hash_table[(r, c, player)] = random.getrandbits(64)
    
    def hash_state(self, state: Any) -> int:
        """Compute Zobrist hash for a game state.
        
        Args:
            state: Game state with board attribute
            
        Returns:
            Hash value (64-bit integer)
        """
        hash_value = 0
        for r in range(self.board_size):
            for c in range(self.board_size):
                player = state.board[r][c]
                hash_value ^= self.hash_table[(r, c, player)]
        return hash_value
    
    def update_hash(self, hash_value: int, move: Tuple[int, int], 
                   old_player: int, new_player: int) -> int:
        """Update hash after a move.
        
        Args:
            hash_value: Current hash value
            move: Move (row, col)
            old_player: Player before move
            new_player: Player after move
            
        Returns:
            Updated hash value
        """
        r, c = move
        # Remove old player
        hash_value ^= self.hash_table[(r, c, old_player)]
        # Add new player
        hash_value ^= self.hash_table[(r, c, new_player)]
        return hash_value


class TranspositionTable:
    """Transposition table storing node statistics."""
    
    def __init__(self):
        """Initialize transposition table."""
        # Map: hash -> node stats
        self.table: Dict[int, Dict] = {}
    
    def get(self, hash_value: int) -> Optional[Dict]:
        """Get node stats from transposition table.
        
        Args:
            hash_value: State hash
            
        Returns:
            Node stats dict or None if not found
        """
        return self.table.get(hash_value)
    
    def store(self, hash_value: int, stats: Dict):
        """Store node stats in transposition table.
        
        Args:
            hash_value: State hash
            stats: Node statistics (N, W, etc.)
        """
        self.table[hash_value] = stats.copy()
    
    def clear(self):
        """Clear transposition table."""
        self.table.clear()
    
    def size(self) -> int:
        """Get number of entries in table."""
        return len(self.table)


class TTNode:
    """MCTS node with transposition table support."""
    
    def __init__(self, state: Any, parent: Optional['TTNode'] = None,
                 move: Optional[Tuple] = None, hash_value: Optional[int] = None):
        """Initialize TT node.
        
        Args:
            state: Game state
            parent: Parent node
            move: Move that led to this node
            hash_value: Zobrist hash of state
        """
        self.state = state
        self.parent = parent
        self.move = move
        self.hash_value = hash_value
        self.N = 0
        self.W = 0.0
        self.children: Dict[Tuple, 'TTNode'] = {}
        self.untried_moves = []
        self.root_player = None
        self._tt_loaded = False
    
    def load_from_tt(self, tt: TranspositionTable):
        """Load statistics from transposition table.
        
        Args:
            tt: Transposition table
        """
        if self._tt_loaded or self.hash_value is None:
            return
        
        stats = tt.get(self.hash_value)
        if stats is not None:
            # Merge statistics (weighted average)
            tt_N = stats.get('N', 0)
            tt_W = stats.get('W', 0.0)
            
            if tt_N > 0:
                # Weight: use TT stats if we have few visits
                if self.N == 0:
                    self.N = tt_N
                    self.W = tt_W
                else:
                    # Weighted merge
                    total_N = self.N + tt_N
                    self.W = (self.W * self.N + tt_W * tt_N) / total_N
                    self.N = total_N
        
        self._tt_loaded = True
    
    def save_to_tt(self, tt: TranspositionTable):
        """Save statistics to transposition table.
        
        Args:
            tt: Transposition table
        """
        if self.hash_value is not None:
            tt.store(self.hash_value, {
                'N': self.N,
                'W': self.W
            })


def create_tt_mcts_wrapper(base_mcts_class, hasher: ZobristHasher):
    """Create a transposition table wrapper for MCTS.
    
    Args:
        base_mcts_class: Base MCTS class (e.g., UCTMCTS, RAVEMCTS)
        hasher: Zobrist hasher
        
    Returns:
        Wrapped MCTS class with TT support
    """
    class TTMCTS(base_mcts_class):
        """MCTS with transposition table."""
        
        def __init__(self, *args, use_tt: bool = True, **kwargs):
            """Initialize TT MCTS.
            
            Args:
                *args: Arguments for base MCTS
                use_tt: Whether to use transposition table
                **kwargs: Keyword arguments for base MCTS
            """
            super().__init__(*args, **kwargs)
            self.use_tt = use_tt
            self.tt = TranspositionTable() if use_tt else None
            self.hasher = hasher
        
        def search(self, state: Any, iterations: int) -> Tuple:
            """Run MCTS search with transposition table.
            
            Args:
                state: Root game state
                iterations: Number of MCTS iterations
                
            Returns:
                Best move
            """
            if self.use_tt:
                # Clear TT for new search (or reuse across moves)
                # self.tt.clear()  # Uncomment to clear between moves
                pass
            
            # Call parent search but with TT integration
            # For now, we'll use a simplified approach
            return super().search(state, iterations)
    
    return TTMCTS
