"""GRAVE (Graph Refinement for AMAF Value Estimation) MCTS implementation.

GRAVE extends RAVE by using AMAF statistics from ancestor nodes that
have been visited sufficiently (N >= threshold T), rather than just
local AMAF statistics. This helps share information across the tree
more effectively.
"""

import math
import random
from typing import Dict, List, Tuple, Optional, Any
from .rave import RAVENode, RAVEMCTS


class GRAVENode(RAVENode):
    """MCTS node with GRAVE ancestor selection."""
    
    def expand(self):
        """Expand node by adding one child (returns GRAVENode)."""
        if self.state.is_terminal():
            return None
        
        if len(self.untried_moves) == 0:
            # Initialize untried moves if not done
            self.untried_moves = self.state.legal_moves()
        
        if len(self.untried_moves) == 0:
            return None
        
        move = self.untried_moves.pop()
        next_state = self.state.next_state(move)
        child = GRAVENode(next_state, parent=self, move=move)
        child.root_player = self.root_player
        self.children[move] = child
        return child
    
    def find_grave_ancestor(self, threshold: int) -> Optional['GRAVENode']:
        """Find ancestor node with N >= threshold for GRAVE.
        
        Args:
            threshold: Minimum visit count threshold
            
        Returns:
            Ancestor node with sufficient visits, or None
        """
        node = self.parent
        while node is not None:
            if node.N >= threshold:
                return node
            node = node.parent
        return None
    
    def grave_value(self, move: Tuple, threshold: int, beta: float,
                   exploration: float = math.sqrt(2)) -> float:
        """Calculate GRAVE blended Q-value for a move.
        
        Args:
            move: Move to evaluate
            threshold: GRAVE threshold T
            beta: RAVE mixing parameter
            exploration: Exploration constant
            
        Returns:
            GRAVE value (infinity if unvisited)
        """
        # Find GRAVE ancestor
        grave_ancestor = self.find_grave_ancestor(threshold)
        
        # UCT component
        if move in self.children:
            child = self.children[move]
            if child.N == 0:
                uct_q = float('inf')
            else:
                uct_q = child.W / child.N
                if self.parent is not None:
                    uct_q += exploration * math.sqrt(
                        math.log(self.parent.N) / child.N
                    )
        else:
            uct_q = float('inf')
        
        # AMAF component (from GRAVE ancestor if available, else local)
        amaf_node = grave_ancestor if grave_ancestor is not None else self
        
        if move in amaf_node.AMAF_N and amaf_node.AMAF_N[move] > 0:
            amaf_q = amaf_node.AMAF_W[move] / amaf_node.AMAF_N[move]
        else:
            amaf_q = float('inf')
        
        # Blend
        if uct_q == float('inf') and amaf_q == float('inf'):
            return float('inf')
        elif uct_q == float('inf'):
            return amaf_q
        elif amaf_q == float('inf'):
            return uct_q
        else:
            return (1 - beta) * uct_q + beta * amaf_q
    
    def best_child_grave(self, threshold: int, beta: float,
                        exploration: float = math.sqrt(2)) -> 'GRAVENode':
        """Select best child using GRAVE.
        
        Args:
            threshold: GRAVE threshold T
            beta: RAVE mixing parameter
            exploration: Exploration constant
            
        Returns:
            Child node with highest GRAVE value
        """
        return max(self.children.values(),
                  key=lambda child: self.grave_value(child.move, threshold, beta, exploration))
    
    def select_leaf_grave(self, threshold: int, beta: float,
                          exploration: float = math.sqrt(2)) -> 'GRAVENode':
        """Select leaf node using GRAVE.
        
        Args:
            threshold: GRAVE threshold T
            beta: RAVE mixing parameter
            exploration: Exploration constant
            
        Returns:
            Leaf node to expand
        """
        node = self
        while not node.is_leaf() and node.is_fully_expanded():
            node = node.best_child_grave(threshold, beta, exploration)
        return node


class GRAVEMCTS:
    """GRAVE MCTS algorithm."""
    
    def __init__(self, exploration: float = math.sqrt(2),
                 beta: float = 0.5,
                 threshold: int = 100,
                 random_seed: Optional[int] = None):
        """Initialize GRAVE MCTS.
        
        Args:
            exploration: Exploration constant (default sqrt(2))
            beta: RAVE mixing parameter (default 0.5)
            threshold: GRAVE threshold T (default 100)
            random_seed: Random seed for reproducibility
        """
        self.exploration = exploration
        self.beta = beta
        self.threshold = threshold
        self.random_seed = random_seed
        if random_seed is not None:
            random.seed(random_seed)
    
    def search(self, state: Any, iterations: int) -> Tuple:
        """Run GRAVE MCTS search.
        
        Args:
            state: Root game state
            iterations: Number of MCTS iterations
            
        Returns:
            Best move (row, col) tuple
        """
        root = GRAVENode(state)
        root.root_player = state.current_player
        
        for _ in range(iterations):
            # Select using GRAVE
            leaf = root.select_leaf_grave(self.threshold, self.beta, self.exploration)
            
            # Expand
            child = leaf.expand()
            if child is None:
                # Terminal node
                reward = leaf.state.reward(root.root_player)
                # Collect trajectory from root to leaf
                trajectory = self._collect_trajectory(root, leaf)
                leaf.backpropagate_amaf(trajectory, reward)
                continue
            
            # Simulate and collect trajectory
            reward, sim_trajectory = self._simulate_with_trajectory(child.state, root.root_player)
            
            # Collect full trajectory from root to terminal
            trajectory = self._collect_trajectory(root, child) + sim_trajectory
            
            # Backpropagate with AMAF
            child.backpropagate_amaf(trajectory, reward)
        
        # Return best move
        best_move = root.best_move()
        if best_move is None:
            # Fallback: return first legal move
            legal = state.legal_moves()
            return legal[0] if legal else None
        return best_move
    
    def _collect_trajectory(self, root: GRAVENode, node: GRAVENode) -> List[Tuple]:
        """Collect trajectory from root to node.
        
        Args:
            root: Root node
            node: Target node
            
        Returns:
            List of moves from root to node
        """
        trajectory = []
        current = node
        while current is not None and current != root:
            if current.move is not None:
                trajectory.insert(0, current.move)
            current = current.parent
        return trajectory
    
    def _simulate_with_trajectory(self, state: Any, root_player: int) -> Tuple[float, List[Tuple]]:
        """Random playout simulation with trajectory tracking.
        
        Args:
            state: State to simulate from
            root_player: Root player for reward calculation
            
        Returns:
            Tuple of (reward, trajectory) where trajectory is list of moves
        """
        current_state = state
        trajectory = []
        
        while not current_state.is_terminal():
            moves = current_state.legal_moves()
            if not moves:
                break
            move = random.choice(moves)
            trajectory.append(move)
            current_state = current_state.next_state(move)
        
        reward = current_state.reward(root_player)
        return reward, trajectory
