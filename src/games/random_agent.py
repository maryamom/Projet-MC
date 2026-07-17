"""Random agent for baseline comparisons."""

import random
from typing import Tuple, Optional
from .hex import HexState


class RandomAgent:
    """Random agent that plays legal moves uniformly at random."""
    
    def __init__(self, random_seed: Optional[int] = None):
        """Initialize random agent.
        
        Args:
            random_seed: Random seed for reproducibility
        """
        self.random_seed = random_seed
        if random_seed is not None:
            random.seed(random_seed)
    
    def play(self, state: HexState) -> Tuple:
        """Play a random legal move.
        
        Args:
            state: Current game state
            
        Returns:
            Random legal move (row, col) tuple
        """
        moves = state.legal_moves()
        if not moves:
            raise ValueError("No legal moves available")
        return random.choice(moves)


def create_random_agent(random_seed: Optional[int] = None):
    """Create a random agent function.
    
    Args:
        random_seed: Random seed
        
    Returns:
        Agent function taking state and returning move
    """
    agent = RandomAgent(random_seed=random_seed)
    return lambda state: agent.play(state)
