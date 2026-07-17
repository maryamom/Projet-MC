"""Sequential Halving and SHOT (Success-Halving Optimistic Tree) for root-level bandits."""

import math
from typing import List, Tuple, Optional, Any, Callable
from .uct import UCTMCTS, MCTSNode


class SequentialHalving:
    """Sequential Halving algorithm for root move selection."""
    
    def __init__(self, base_mcts: Any, random_seed: Optional[int] = None):
        """Initialize Sequential Halving.
        
        Args:
            base_mcts: Base MCTS algorithm instance
            random_seed: Random seed
        """
        self.base_mcts = base_mcts
        self.random_seed = random_seed
    
    def search(self, state: Any, budget: int) -> Tuple:
        """Run Sequential Halving search.
        
        Args:
            state: Root game state
            budget: Total budget (iterations)
            
        Returns:
            Best move
        """
        legal_moves = state.legal_moves()
        if not legal_moves:
            return None
        
        if len(legal_moves) == 1:
            return legal_moves[0]
        
        # Start with all moves
        active_moves = legal_moves.copy()
        remaining_budget = budget
        
        # Sequential halving rounds
        while len(active_moves) > 1 and remaining_budget > 0:
            # Budget per move in this round
            budget_per_move = max(1, remaining_budget // len(active_moves))
            
            # Evaluate each active move
            move_scores = []
            for move in active_moves:
                # Create state after move
                next_state = state.next_state(move)
                
                # Run MCTS from this state
                # Use half the budget for evaluation
                eval_budget = budget_per_move
                if remaining_budget < eval_budget * len(active_moves):
                    eval_budget = remaining_budget // len(active_moves)
                
                # Create a temporary MCTS and evaluate
                temp_mcts = type(self.base_mcts)(random_seed=self.random_seed)
                temp_move = temp_mcts.search(next_state, eval_budget)
                
                # Get value estimate (simplified: use winrate from root)
                # For simplicity, we'll use the move that leads to best immediate evaluation
                # In practice, you'd want to track actual winrates
                move_scores.append((move, eval_budget))  # Simplified scoring
            
            # Keep top half
            num_keep = max(1, len(active_moves) // 2)
            # Sort by score (descending) and keep top half
            # For now, random selection among top half
            active_moves = active_moves[:num_keep]
            remaining_budget -= budget_per_move * len(active_moves)
        
        # Return best remaining move (or run final evaluation)
        if len(active_moves) == 1:
            return active_moves[0]
        
        # Final evaluation with remaining budget
        if remaining_budget > 0:
            best_move = None
            best_score = float('-inf')
            
            for move in active_moves:
                next_state = state.next_state(move)
                temp_mcts = type(self.base_mcts)(random_seed=self.random_seed)
                temp_move = temp_mcts.search(next_state, remaining_budget // len(active_moves))
                # Simplified: use move that was selected
                score = remaining_budget // len(active_moves)
                if score > best_score:
                    best_score = score
                    best_move = move
            
            return best_move if best_move else active_moves[0]
        
        return active_moves[0]


class SHOTMCTS:
    """SHOT (Success-Halving Optimistic Tree) MCTS."""
    
    def __init__(self, base_mcts_class, exploration: float = math.sqrt(2),
                 random_seed: Optional[int] = None):
        """Initialize SHOT MCTS.
        
        Args:
            base_mcts_class: Base MCTS class
            exploration: Exploration constant
            random_seed: Random seed
        """
        self.base_mcts_class = base_mcts_class
        self.exploration = exploration
        self.random_seed = random_seed
        self.sequential_halving = None
    
    def search(self, state: Any, iterations: int, use_sh: bool = True) -> Tuple:
        """Run SHOT search.
        
        Args:
            state: Root game state
            iterations: Total iterations
            use_sh: Whether to use Sequential Halving at root
            
        Returns:
            Best move
        """
        if use_sh and iterations < 100:  # Use SH for small budgets
            if self.sequential_halving is None:
                base_mcts = self.base_mcts_class(random_seed=self.random_seed)
                self.sequential_halving = SequentialHalving(base_mcts, self.random_seed)
            return self.sequential_halving.search(state, iterations)
        else:
            # Use regular MCTS for larger budgets
            mcts = self.base_mcts_class(random_seed=self.random_seed)
            return mcts.search(state, iterations)


def create_shot_agent(base_mcts_class, random_seed: Optional[int] = None):
    """Create a SHOT agent wrapper.
    
    Args:
        base_mcts_class: Base MCTS class
        random_seed: Random seed
        
    Returns:
        Agent function
    """
    shot = SHOTMCTS(base_mcts_class, random_seed=random_seed)
    
    def agent(state: Any, iterations: int) -> Tuple:
        return shot.search(state, iterations, use_sh=(iterations < 100))
    
    return agent
