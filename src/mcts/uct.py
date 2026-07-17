"""UCT (Upper Confidence bounds applied to Trees) MCTS implementation.

This module provides a generic UCT MCTS implementation that works with
any game that exposes the required interface:
- legal_moves(state)
- next_state(state, move)
- is_terminal(state)
- reward(state, root_player)
"""

import math
import random
from typing import Dict, List, Tuple, Optional, Callable, Any
from collections import defaultdict


class MCTSNode:
    """MCTS node with statistics."""
    
    def __init__(self, state: Any, parent: Optional['MCTSNode'] = None, 
                 move: Optional[Tuple] = None):
        """Initialize MCTS node.
        
        Args:
            state: Game state
            parent: Parent node (None for root)
            move: Move that led to this node
        """
        self.state = state
        self.parent = parent
        self.move = move
        self.N = 0  # Visit count
        self.W = 0.0  # Total reward
        self.children: Dict[Tuple, 'MCTSNode'] = {}
        self.untried_moves: List[Tuple] = []
        self.root_player = None  # Will be set at root
    
    def is_fully_expanded(self) -> bool:
        """Check if all moves have been tried."""
        return len(self.untried_moves) == 0
    
    def is_leaf(self) -> bool:
        """Check if node is a leaf (no children)."""
        return len(self.children) == 0
    
    def uct_value(self, exploration: float = math.sqrt(2)) -> float:
        """Calculate UCT value for selection.
        
        Args:
            exploration: Exploration constant (default sqrt(2))
            
        Returns:
            UCT value (infinity if unvisited)
        """
        if self.N == 0:
            return float('inf')
        
        exploitation = self.W / self.N
        if self.parent is None:
            return exploitation
        
        exploration_term = exploration * math.sqrt(
            math.log(self.parent.N) / self.N
        )
        return exploitation + exploration_term
    
    def best_child(self, exploration: float = math.sqrt(2)) -> 'MCTSNode':
        """Select best child using UCT.
        
        Args:
            exploration: Exploration constant
            
        Returns:
            Child node with highest UCT value
        """
        return max(self.children.values(), 
                  key=lambda child: child.uct_value(exploration))
    
    def select_leaf(self, exploration: float = math.sqrt(2)) -> 'MCTSNode':
        """Select leaf node using UCT.
        
        Args:
            exploration: Exploration constant
            
        Returns:
            Leaf node to expand
        """
        node = self
        while not node.is_leaf() and node.is_fully_expanded():
            node = node.best_child(exploration)
        return node
    
    def expand(self) -> Optional['MCTSNode']:
        """Expand node by adding one child.
        
        Returns:
            New child node, or None if terminal/no moves
        """
        if self.state.is_terminal():
            return None
        
        if len(self.untried_moves) == 0:
            # Initialize untried moves if not done
            self.untried_moves = self.state.legal_moves()
        
        if len(self.untried_moves) == 0:
            return None
        
        move = self.untried_moves.pop()
        next_state = self.state.next_state(move)
        child = MCTSNode(next_state, parent=self, move=move)
        child.root_player = self.root_player
        self.children[move] = child
        return child
    
    def backpropagate(self, reward: float):
        """Backpropagate reward up the tree.
        
        Args:
            reward: Reward from simulation (from root_player's perspective)
        """
        node = self
        while node is not None:
            node.N += 1
            node.W += reward
            node = node.parent
    
    def best_move(self) -> Optional[Tuple]:
        """Get best move from this node.
        
        Returns:
            Move with highest visit count, or None if no children
        """
        if not self.children:
            return None
        return max(self.children.items(), key=lambda x: x[1].N)[0]


class UCTMCTS:
    """UCT MCTS algorithm."""
    
    def __init__(self, exploration: float = math.sqrt(2), 
                 random_seed: Optional[int] = None):
        """Initialize UCT MCTS.
        
        Args:
            exploration: Exploration constant (default sqrt(2))
            random_seed: Random seed for reproducibility
        """
        self.exploration = exploration
        self.random_seed = random_seed
        if random_seed is not None:
            random.seed(random_seed)
    
    def search(self, state: Any, iterations: int) -> Tuple:
        """Run MCTS search.
        
        Args:
            state: Root game state
            iterations: Number of MCTS iterations
            
        Returns:
            Best move (row, col) tuple
        """
        root = MCTSNode(state)
        root.root_player = state.current_player
        
        for _ in range(iterations):
            # Select
            leaf = root.select_leaf(self.exploration)
            
            # Expand
            child = leaf.expand()
            if child is None:
                # Terminal node
                reward = leaf.state.reward(root.root_player)
                leaf.backpropagate(reward)
                continue
            
            # Simulate
            reward = self._simulate(child.state, root.root_player)
            
            # Backpropagate
            child.backpropagate(reward)
        
        # Return best move
        best_move = root.best_move()
        if best_move is None:
            # Fallback: return first legal move
            legal = state.legal_moves()
            return legal[0] if legal else None
        return best_move
    
    def _simulate(self, state: Any, root_player: int) -> float:
        """Random playout simulation.
        
        Args:
            state: State to simulate from
            root_player: Root player for reward calculation
            
        Returns:
            Reward from root_player's perspective
        """
        current_state = state
        while not current_state.is_terminal():
            moves = current_state.legal_moves()
            if not moves:
                break
            move = random.choice(moves)
            current_state = current_state.next_state(move)
        
        return current_state.reward(root_player)
