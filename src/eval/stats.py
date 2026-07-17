"""Statistical utilities for experiment analysis."""

import math
from typing import Tuple


def wilson_interval(wins: int, total: int, confidence: float = 0.95) -> Tuple[float, float]:
    """Calculate Wilson confidence interval for binomial proportion.
    
    Args:
        wins: Number of wins
        total: Total number of games
        confidence: Confidence level (default 0.95 for 95% CI)
        
    Returns:
        Tuple of (lower_bound, upper_bound)
    """
    if total == 0:
        return (0.0, 1.0)
    
    z = 1.96 if confidence == 0.95 else 2.576 if confidence == 0.99 else 1.645
    
    p = wins / total
    denominator = 1 + (z**2 / total)
    center = (p + (z**2 / (2 * total))) / denominator
    margin = (z / denominator) * math.sqrt((p * (1 - p) / total) + (z**2 / (4 * total**2)))
    
    lower = max(0.0, center - margin)
    upper = min(1.0, center + margin)
    
    return (lower, upper)


def elo_estimate(wins: int, losses: int, draws: int = 0, k: float = 32.0) -> float:
    """Estimate Elo difference between two players.
    
    Args:
        wins: Number of wins for player 1
        losses: Number of losses for player 1
        draws: Number of draws
        k: K-factor for Elo calculation (default 32)
        
    Returns:
        Estimated Elo difference (positive means player 1 is stronger)
    """
    total = wins + losses + draws
    if total == 0:
        return 0.0
    
    score = wins + (draws * 0.5)
    expected_score = score / total
    
    # Elo difference formula: ΔE = 400 * log10(W/L) if no draws
    # More general: ΔE = 400 * log10((score - draws*0.5) / (total - score - draws*0.5))
    if wins + losses > 0:
        win_rate = wins / (wins + losses)
        if win_rate == 0:
            return -400.0  # Very large negative difference
        elif win_rate == 1:
            return 400.0   # Very large positive difference
        else:
            return 400 * math.log10(win_rate / (1 - win_rate))
    
    return 0.0  # Only draws


def binomial_test(wins: int, total: int, p_null: float = 0.5) -> float:
    """Perform binomial test for winrate significance.
    
    Args:
        wins: Number of wins
        total: Total number of games
        p_null: Null hypothesis probability (default 0.5 for equal strength)
        
    Returns:
        p-value (probability of observing this result under null hypothesis)
    """
    # Simplified binomial test using normal approximation
    if total == 0:
        return 1.0
    
    p_obs = wins / total
    se = math.sqrt(p_null * (1 - p_null) / total)
    z = (p_obs - p_null) / se if se > 0 else 0
    
    # Two-tailed test using error function approximation
    # P(|Z| > z) ≈ 2 * (1 - Φ(|z|)) where Φ is standard normal CDF
    # Using approximation: Φ(x) ≈ 0.5 * (1 + erf(x/√2))
    erf_approx = 1 - math.exp(-z*z/2) * (0.7978845608 - 0.356563782*z*z + 0.319381530*z*z*z*z)
    p_value = 2 * (1 - 0.5 * (1 + erf_approx)) if z >= 0 else 2 * (1 - 0.5 * (1 - erf_approx))
    return max(0.0, min(1.0, p_value))
