import numpy as np
import pandas as pd
from scipy.stats import norm

def black_scholes(option_type, K, S, r, T, sigma, q=0.0, precision=4, show_table=False):
    """
    Calculate Black-Scholes option prices and Greeks.

    Parameters:
    - option_type (str or list of str): Types: 'call', 'put', 'forward', 'binary_call', 'binary_put'
    - K (float): Strike price
    - S (float): Spot price
    - r (float): Risk-free rate
    - T (float): Time to maturity (in years)
    - sigma (float): Volatility
    - q (float): Dividend yield (default 0.0)
    - precision (int): Decimal places to round to
    - show_table (bool): Whether to print a DataFrame

    Returns:
    - dict or DataFrame: Option prices and Greeks
    """
    if K <= 0:
        raise ValueError("Strike price (K) must be greater than 0.")
    if S <= 0:
        raise ValueError("Spot price (S) must be greater than 0.")
    if r < 0:
        raise ValueError("Risk-free rate (r) must be non-negative.")
    if T <= 0:
        raise ValueError("Time to maturity (T) must be greater than 0.")
    if sigma <= 0:
        raise ValueError("Volatility (sigma) must be greater than 0.")
    if q < 0:
        raise ValueError("Dividend yield (q) must be non-negative.")
    

    if isinstance(option_type, str):
        option_type = [option_type]

    d1 = (np.log(S / K) + (r - q + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    phi_d1 = norm.pdf(d1)
    phi_d2 = norm.pdf(d2)
    Nd1, Nd2 = norm.cdf(d1), norm.cdf(d2)
    Nmd1, Nmd2 = norm.cdf(-d1), norm.cdf(-d2)

    results = {'Price': {}, 'Delta': {}, 'Gamma': {}, 'Vega': {}, 'Rho': {}, 'Theta': {}}

    for opt in option_type:
        if opt == 'call':
            price = S * np.exp(-q * T) * Nd1 - K * np.exp(-r * T) * Nd2
            delta = np.exp(-q * T) * Nd1
            gamma = (np.exp(-q * T) * phi_d1) / (S * sigma * np.sqrt(T))
            vega = S * np.exp(-q * T) * phi_d1 * np.sqrt(T)
            rho = K * T * np.exp(-r * T) * Nd2
            theta = (
                -S * sigma * np.exp(-q * T) * phi_d1 / (2 * np.sqrt(T))
                - r * K * np.exp(-r * T) * Nd2
                + q * S * np.exp(-q * T) * Nd1
            )

        elif opt == 'put':
            price = K * np.exp(-r * T) * Nmd2 - S * np.exp(-q * T) * Nmd1
            delta = -np.exp(-q * T) * Nmd1
            gamma = (np.exp(-q * T) * phi_d1) / (S * sigma * np.sqrt(T))
            vega = S * np.exp(-q * T) * phi_d1 * np.sqrt(T)
            rho = -K * T * np.exp(-r * T) * Nmd2
            theta = (
                -S * sigma * np.exp(-q * T) * phi_d1 / (2 * np.sqrt(T))
                + r * K * np.exp(-r * T) * Nmd2
                - q * S * np.exp(-q * T) * Nmd1
            )

        elif opt == 'forward':
            price = S * np.exp(-q * T) - K * np.exp(-r * T)
            delta = np.exp(-q * T)
            gamma = 0.0
            vega = 0.0
            rho = K * T * np.exp(-r * T)
            theta = q * S * np.exp(-q * T) - r * K * np.exp(-r * T)

        elif opt == 'binary_call':
            price = np.exp(-r * T) * Nd2
            delta = (np.exp(-r * T) * phi_d2) / (S * sigma * np.sqrt(T))
            gamma = -(np.exp(-r * T) * phi_d2 * d1) / (S**2 * sigma**2 * T)
            vega = -np.exp(-r * T) * phi_d2 * d1 / sigma
            rho = -T * np.exp(-r * T) * Nd2 + np.exp(-r * T) * phi_d2 * np.sqrt(T) / sigma
            theta = -np.exp(-r * T) * (
                -r * Nd2 + phi_d2 * ((r - q - 0.5 * sigma**2) / (sigma * np.sqrt(T)) - d2 / (2 * T))
            )

        elif opt == 'binary_put':
            price = np.exp(-r * T) * Nmd2
            delta = -(np.exp(-r * T) * phi_d2) / (S * sigma * np.sqrt(T))
            gamma = (np.exp(-r * T) * phi_d2 * d1) / (S**2 * sigma**2 * T)
            vega = np.exp(-r * T) * phi_d2 * d1 / sigma
            rho = -T * np.exp(-r * T) * Nmd2 - np.exp(-r * T) * phi_d2 * np.sqrt(T) / sigma
            theta = -np.exp(-r * T) * (
                -r * Nmd2 + phi_d2 * (-(r - q - 0.5 * sigma**2) / (sigma * np.sqrt(T)) + d2 / (2 * T))
            )

        else:
            raise ValueError(f"Unknown option type: {opt}")

        label = opt.replace('_', ' ').title()
        results['Price'][label] = round(price, precision)
        results['Delta'][label] = round(delta, precision)
        results['Gamma'][label] = round(gamma, precision)
        results['Vega'][label] = round(vega, precision)
        results['Rho'][label] = round(rho, precision)
        results['Theta'][label] = round(theta, precision)

    df = pd.DataFrame(results).T
    if show_table:
        print(df)
    return df
