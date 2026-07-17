"""RAVE (Rapid Action Value Estimation) MCTS implementation.

RAVE extends UCT by maintaining AMAF (All Moves As First) statistics,
which track how good moves are regardless of when they were played in
the simulation. This helps in games like Hex where move order matters
less than move quality.
"""

import math
import random
from typing import Dict, List, Tuple, Optional, Any
from .uct import MCTSNode, UCTMCTS


class RAVENode(MCTSNode):
    """MCTS node with AMAF statistics for RAVE."""
    
    def __init__(self, state: Any, parent: Optional['RAVENode'] = None,
                 move: Optional[Tuple] = None):
        """Initialize RAVE node.
        
        Args:
            state: Game state
            parent: Parent node (None for root)
            move: Move that led to this node
        """
        super().__init__(state, parent, move)
        # AMAF statistics: per-move visit count and total reward
        self.AMAF_N: Dict[Tuple, int] = {}  # AMAF visit count per move
        self.AMAF_W: Dict[Tuple, float] = {}  # AMAF total reward per move
    
    def expand(self) -> Optional['RAVENode']:
        """Expand node by adding one child (returns RAVENode)."""
        if self.state.is_terminal():
            return None
        
        if len(self.untried_moves) == 0:
            # Initialize untried moves if not done
            self.untried_moves = self.state.legal_moves()
        
        if len(self.untried_moves) == 0:
            return None
        
        move = self.untried_moves.pop()
        next_state = self.state.next_state(move)
        child = RAVENode(next_state, parent=self, move=move)
        child.root_player = self.root_player
        self.children[move] = child
        return child
    
    def update_amaf(self, moves: List[Tuple], reward: float):
        """Update AMAF statistics for moves in simulation trajectory.
        
        Args:
            moves: List of moves played in simulation
            reward: Reward from simulation (from root_player's perspective)
        """
        for move in moves:
            if move not in self.AMAF_N:
                self.AMAF_N[move] = 0
                self.AMAF_W[move] = 0.0
            self.AMAF_N[move] += 1
            self.AMAF_W[move] += reward
    
    def rave_value(self, move: Tuple, beta: float, exploration: float = math.sqrt(2)) -> float:
        """Calculate RAVE blended Q-value for a move.
        
        Args:
            move: Move to evaluate
            beta: RAVE mixing parameter (0 = pure UCT, 1 = pure AMAF)
            exploration: Exploration constant
            
        Returns:
            RAVE value (infinity if unvisited)
        """
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
        
        # AMAF component
        if move in self.AMAF_N and self.AMAF_N[move] > 0:
            amaf_q = self.AMAF_W[move] / self.AMAF_N[move]
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
    
    def best_child_rave(self, beta: float, exploration: float = math.sqrt(2)) -> 'RAVENode':
        """Select best child using RAVE.
        
        Args:
            beta: RAVE mixing parameter
            exploration: Exploration constant
            
        Returns:
            Child node with highest RAVE value
        """
        return max(self.children.values(),
                  key=lambda child: self.rave_value(child.move, beta, exploration))
    
    def select_leaf_rave(self, beta: float, exploration: float = math.sqrt(2)) -> 'RAVENode':
        """Select leaf node using RAVE.
        
        Args:
            beta: RAVE mixing parameter
            exploration: Exploration constant
            
        Returns:
            Leaf node to expand
        """
        node = self
        while not node.is_leaf() and node.is_fully_expanded():
            node = node.best_child_rave(beta, exploration)
        return node
    
    def backpropagate_amaf(self, trajectory: List[Tuple], reward: float):
        """Backpropagate reward and update AMAF statistics.
        
        Args:
            trajectory: List of moves played in simulation
            reward: Reward from simulation (from root_player's perspective)
        """
        node = self
        while node is not None:
            node.N += 1
            node.W += reward
            # Update AMAF for this node
            node.update_amaf(trajectory, reward)
            node = node.parent


class RAVEMCTS:
    """RAVE MCTS algorithm."""
    
    def __init__(self, exploration: float = math.sqrt(2),
                 beta: float = 0.5,
                 random_seed: Optional[int] = None):
        """Initialize RAVE MCTS.
        
        Args:
            exploration: Exploration constant (default sqrt(2))
            beta: RAVE mixing parameter (default 0.5)
            random_seed: Random seed for reproducibility
        """
        self.exploration = exploration
        self.beta = beta
        self.random_seed = random_seed
        if random_seed is not None:
            random.seed(random_seed)
    
    def _compute_beta(self, node: RAVENode) -> float:
        """Compute adaptive beta value.
        
        Beta decreases as node visits increase, transitioning from
        AMAF-heavy to UCT-heavy.
        
        Args:
            node: Node to compute beta for
            
        Returns:
            Adaptive beta value
        """
        if node.N == 0:
            return self.beta
        # Beta decreases as sqrt(k) / (3*sqrt(k) + N)
        # where k is a constant (typically move count)
        k = 1000  # Typical value
        return math.sqrt(k) / (3 * math.sqrt(k) + node.N)
    
    def search(self, state: Any, iterations: int) -> Tuple:
        """Run RAVE MCTS search.
        
        Args:
            state: Root game state
            iterations: Number of MCTS iterations
            
        Returns:
            Best move (row, col) tuple
        """
        root = RAVENode(state)
        root.root_player = state.current_player
        
        for _ in range(iterations):
            # Select using RAVE
            leaf = root.select_leaf_rave(self.beta, self.exploration)
            
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
    
    def _collect_trajectory(self, root: RAVENode, node: RAVENode) -> List[Tuple]:
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
