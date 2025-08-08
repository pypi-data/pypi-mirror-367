def validate_inputs(S, K, T, r, sigma, q):
    if S <= 0: raise ValueError("Spot price must be positive.")
    if K <= 0: raise ValueError("Strike must be positive.")
    if T <= 0: raise ValueError("Maturity must be positive.")
    if sigma <= 0: raise ValueError("Volatility must be positive.")
    if r < 0: raise ValueError("Risk-free rate cannot be negative.")
    if q < 0: raise ValueError("Dividend yield cannot be negative.")