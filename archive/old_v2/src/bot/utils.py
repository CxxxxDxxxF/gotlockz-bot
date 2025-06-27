def kelly_fraction(prob: float, odds: float) -> float:
    """
    Calculate the Kelly fraction for optimal bet sizing.
    prob: your estimated probability (e.g., 0.58 for 58%)
    odds: decimal odds (e.g., 2.20 for +120 American odds)
    returns: fraction of bankroll to bet (can be negative if no edge)
    """
    if odds <= 1:
        return 0.0
    edge = prob * (odds - 1) - (1 - prob)
    denom = odds - 1
    kelly = edge / denom
    return max(0.0, kelly)  # Never bet negative fraction
