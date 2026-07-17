"""PUCT (Predictor + UCT) MCTS implementation.

PUCT uses prior probabilities and value estimates from a "network"
(in this case, a toy heuristic function) to guide search.
"""

import math
import random
from typing import Dict, List, Tuple, Optional, Any
from .uct import MCTSNode, UCTMCTS


def policy_value_toy_network(state: Any) -> Tuple[Dict[Tuple, float], float]:
    """Toy policy/value network for Hex.
    
    Returns:
        Tuple of (priors_dict, value_estimate)
        - priors_dict: Dictionary mapping moves to prior probabilities
        - value_estimate: State value estimate in [-1, 1]
    """
    size = state.size
    legal_moves = state.legal_moves()
    
    if not legal_moves:
        return {}, 0.0
    
    # Center bias: prefer moves near center
    priors = {}
    center = (size - 1) / 2
    
    for move in legal_moves:
        r, c = move
        # Distance from center (normalized)
        dist_r = abs(r - center) / size
        dist_c = abs(c - center) / size
        dist = math.sqrt(dist_r**2 + dist_c**2)
        
        # Center bias: higher score for moves closer to center
        center_score = 1.0 - dist
        
        # Add small random noise
        noise = random.random() * 0.1
        
        priors[move] = center_score + noise
    
    # Normalize priors
    total = sum(priors.values())
    if total > 0:
        priors = {move: prob / total for move, prob in priors.items()}
    else:
        # Uniform if all zero
        uniform_prob = 1.0 / len(legal_moves)
        priors = {move: uniform_prob for move in legal_moves}
    
    # Value estimate: simple connectivity heuristic
    # Count stones near edges for current player
    value = 0.0
    if state.current_player == 1:  # BLACK (top-bottom)
        # Check top and bottom rows
        top_stones = sum(1 for c in range(size) if state.board[0][c] == 1)
        bottom_stones = sum(1 for c in range(size) if state.board[size-1][c] == 1)
        value = (top_stones + bottom_stones) / (2 * size)
    else:  # WHITE (left-right)
        # Check left and right columns
        left_stones = sum(1 for r in range(size) if state.board[r][0] == 2)
        right_stones = sum(1 for r in range(size) if state.board[r][size-1] == 2)
        value = (left_stones + right_stones) / (2 * size)
    
    # Normalize to [-1, 1] and add small random component
    value = (value - 0.5) * 2 + (random.random() - 0.5) * 0.1
    value = max(-1.0, min(1.0, value))
    
    return priors, value


class PUCTNode(MCTSNode):
    """MCTS node with PUCT selection."""
    
    def __init__(self, state: Any, parent: Optional['PUCTNode'] = None,
                 move: Optional[Tuple] = None, prior: float = 1.0):
        """Initialize PUCT node.
        
        Args:
            state: Game state
            parent: Parent node
            move: Move that led to this node
            prior: Prior probability for this move
        """
        super().__init__(state, parent, move)
        self.prior = prior
    
    def puct_value(self, c_puct: float = 1.0) -> float:
        """Calculate PUCT value for selection.
        
        Args:
            c_puct: PUCT exploration constant
            
        Returns:
            PUCT value (infinity if unvisited)
        """
        if self.N == 0:
            return float('inf')
        
        exploitation = self.W / self.N
        
        if self.parent is None:
            return exploitation
        
        # PUCT formula: Q + c_puct * P * sqrt(N_parent) / (1 + N)
        exploration_term = c_puct * self.prior * math.sqrt(self.parent.N) / (1 + self.N)
        
        return exploitation + exploration_term
    
    def best_child_puct(self, c_puct: float = 1.0) -> 'PUCTNode':
        """Select best child using PUCT.
        
        Args:
            c_puct: PUCT exploration constant
            
        Returns:
            Child node with highest PUCT value
        """
        return max(self.children.values(),
                  key=lambda child: child.puct_value(c_puct))
    
    def select_leaf_puct(self, c_puct: float = 1.0) -> 'PUCTNode':
        """Select leaf node using PUCT.
        
        Args:
            c_puct: PUCT exploration constant
            
        Returns:
            Leaf node to expand
        """
        node = self
        while not node.is_leaf() and node.is_fully_expanded():
            node = node.best_child_puct(c_puct)
        return node
    
    def expand(self) -> Optional['PUCTNode']:
        """Expand node by adding one child (returns PUCTNode)."""
        if self.state.is_terminal():
            return None
        
        if len(self.untried_moves) == 0:
            # Initialize untried moves if not done
            self.untried_moves = self.state.legal_moves()
        
        if len(self.untried_moves) == 0:
            return None
        
        move = self.untried_moves.pop()
        next_state = self.state.next_state(move)
        
        # Get prior for this move (if we have priors cached)
        prior = getattr(self, '_move_priors', {}).get(move, 1.0 / len(self.state.legal_moves()))
        
        child = PUCTNode(next_state, parent=self, move=move, prior=prior)
        child.root_player = self.root_player
        self.children[move] = child
        return child


class PUCTMCTS:
    """PUCT MCTS algorithm."""
    
    def __init__(self, c_puct: float = 1.0,
                 policy_value_fn: Optional[callable] = None,
                 use_value_bootstrap: bool = True,
                 random_seed: Optional[int] = None):
        """Initialize PUCT MCTS.
        
        Args:
            c_puct: PUCT exploration constant (default 1.0)
            policy_value_fn: Function(state) -> (priors_dict, value)
            use_value_bootstrap: If True, use value estimate instead of full playout
            random_seed: Random seed for reproducibility
        """
        self.c_puct = c_puct
        self.policy_value_fn = policy_value_fn or policy_value_toy_network
        self.use_value_bootstrap = use_value_bootstrap
        self.random_seed = random_seed
        if random_seed is not None:
            random.seed(random_seed)
    
    def search(self, state: Any, iterations: int) -> Tuple:
        """Run PUCT MCTS search.
        
        Args:
            state: Root game state
            iterations: Number of MCTS iterations
            
        Returns:
            Best move (row, col) tuple
        """
        root = PUCTNode(state)
        root.root_player = state.current_player
        
        # Get priors and value for root
        priors, root_value = self.policy_value_fn(state)
        root._move_priors = priors
        
        for _ in range(iterations):
            # Select using PUCT
            leaf = root.select_leaf_puct(self.c_puct)
            
            # Expand
            child = leaf.expand()
            if child is None:
                # Terminal node
                reward = leaf.state.reward(root.root_player)
                leaf.backpropagate(reward)
                continue
            
            # Get priors for child state
            child_priors, _ = self.policy_value_fn(child.state)
            child._move_priors = child_priors
            
            # Simulate or bootstrap
            if self.use_value_bootstrap:
                # Use value estimate instead of full playout
                _, value_est = self.policy_value_fn(child.state)
                # Convert value estimate to reward from root player's perspective
                reward = value_est if child.state.current_player == root.root_player else -value_est
            else:
                # Short playout (mix of value and simulation)
                reward, _ = self._simulate_with_trajectory(child.state, root.root_player)
            
            # Backpropagate
            child.backpropagate(reward)
        
        # Return best move
        best_move = root.best_move()
        if best_move is None:
            # Fallback: return first legal move
            legal = state.legal_moves()
            return legal[0] if legal else None
        return best_move
    
    def _simulate_with_trajectory(self, state: Any, root_player: int) -> Tuple[float, List[Tuple]]:
        """Short random playout simulation.
        
        Args:
            state: State to simulate from
            root_player: Root player for reward calculation
            
        Returns:
            Tuple of (reward, trajectory)
        """
        current_state = state
        trajectory = []
        max_depth = 10  # Limit simulation depth
        
        depth = 0
        while not current_state.is_terminal() and depth < max_depth:
            moves = current_state.legal_moves()
            if not moves:
                break
            move = random.choice(moves)
            trajectory.append(move)
            current_state = current_state.next_state(move)
            depth += 1
        
        # If not terminal, use value estimate
        if not current_state.is_terminal():
            _, value_est = self.policy_value_fn(current_state)
            reward = value_est if current_state.current_player == root_player else -value_est
        else:
            reward = current_state.reward(root_player)
        
        return reward, trajectory
