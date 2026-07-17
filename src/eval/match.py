"""Match runner for evaluating agents."""

from typing import Callable, Tuple, Optional
from ..games.hex import HexState, Player


def play_match(agent1: Callable[[HexState], Tuple], 
               agent2: Callable[[HexState], Tuple],
               initial_state: HexState,
               verbose: bool = False,
               agent1_starts: bool = True) -> int:
    """Play a match between two agents.
    
    Args:
        agent1: Function taking state, returning move
        agent2: Function taking state, returning move
        initial_state: Starting game state
        verbose: Print moves if True
        agent1_starts: If True, agent1 plays as BLACK (first), else agent2 plays as BLACK
        
    Returns:
        1 if agent1 wins, -1 if agent2 wins, 0 if draw
    """
    state = initial_state
    
    # Swap initial player if agent2 should start
    if not agent1_starts:
        # Create state with WHITE to move first (swap players)
        swapped_board = [[Player.WHITE if cell == Player.BLACK else 
                         Player.BLACK if cell == Player.WHITE else Player.EMPTY
                         for cell in row] for row in state.board]
        state = HexState(state.size, swapped_board, Player.WHITE)
    
    while not state.is_terminal():
        if state.current_player == Player.BLACK:
            move = agent1(state) if agent1_starts else agent2(state)
        else:
            move = agent2(state) if agent1_starts else agent1(state)
        
        if verbose:
            player_str = "BLACK" if state.current_player == Player.BLACK else "WHITE"
            agent_str = "Agent1" if (state.current_player == Player.BLACK and agent1_starts) or \
                                  (state.current_player == Player.WHITE and not agent1_starts) else "Agent2"
            print(f"{agent_str} ({player_str}) plays {move}")
        
        state = state.next_state(move)
    
    # Determine winner and map back to agent perspective
    winner = state._has_winner()
    if winner == Player.BLACK:
        return 1 if agent1_starts else -1
    elif winner == Player.WHITE:
        return -1 if agent1_starts else 1
    else:
        return 0
