import numpy as np
import scipy.stats as stats

# === Helper functions ===
def _d1(S, K, T, r, sigma, q=0.0):
    return (np.log(S / K) + (r - q + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))

def _d2(S, K, T, r, sigma, q=0.0):
    return _d1(S, K, T, r, sigma, q) - sigma * np.sqrt(T)

def _phi_d1(S, K, T, r, sigma, q=0.0):
    return stats.norm.pdf(_d1(S, K, T, r, sigma, q))

def _phi_d2(S, K, T, r, sigma, q=0.0):
    return stats.norm.pdf(_d2(S, K, T, r, sigma, q))

def _Nd1(S, K, T, r, sigma, q=0.0):
    return stats.norm.cdf(_d1(S, K, T, r, sigma, q))

def _Nd2(S, K, T, r, sigma, q=0.0):
    return stats.norm.cdf(_d2(S, K, T, r, sigma, q))

def _Nmd1(S, K, T, r, sigma, q=0.0):
    return stats.norm.cdf(-_d1(S, K, T, r, sigma, q))

def _Nmd2(S, K, T, r, sigma, q=0.0):
    return stats.norm.cdf(-_d2(S, K, T, r, sigma, q))


# === Black-Scholes Call Option ===
def bs_call_price(S, K, T, r, sigma, q=0.0):
    """Calculate Black-Scholes call option price."""
    return S * np.exp(-q * T) * _Nd1(S, K, T, r, sigma, q) - K * np.exp(-r * T) * _Nd2(S, K, T, r, sigma, q)

def bs_call_delta(S, K, T, r, sigma, q=0.0):
    """Calculate Black-Scholes call option delta."""
    return np.exp(-q * T) * _Nd1(S, K, T, r, sigma, q)

def bs_call_gamma(S, K, T, r, sigma, q=0.0):
    """Calculate Black-Scholes call option gamma."""
    return (np.exp(-q * T) * _phi_d1(S, K, T, r, sigma, q)) / (S * sigma * np.sqrt(T))

def bs_call_vega(S, K, T, r, sigma, q=0.0):
    """Calculate Black-Scholes call option vega."""
    return S * np.exp(-q * T) * _phi_d1(S, K, T, r, sigma, q) * np.sqrt(T)

def bs_call_rho(S, K, T, r, sigma, q=0.0):
    """Calculate Black-Scholes call option rho."""
    return K * T * np.exp(-r * T) * _Nd2(S, K, T, r, sigma, q)

def bs_call_theta(S, K, T, r, sigma, q=0.0):
    """Calculate Black-Scholes call option theta."""
    return (
        -S * sigma * np.exp(-q * T) * _phi_d1(S, K, T, r, sigma, q) / (2 * np.sqrt(T))
        - r * K * np.exp(-r * T) * _Nd2(S, K, T, r, sigma, q)
        + q * S * np.exp(-q * T) * _Nd1(S, K, T, r, sigma, q)
    )


# === Black-Scholes Put Option ===
def bs_put_price(S, K, T, r, sigma, q=0.0):
    """Calculate Black-Scholes put option price."""
    return K * np.exp(-r * T) * _Nmd2(S, K, T, r, sigma, q) - S * np.exp(-q * T) * _Nmd1(S, K, T, r, sigma, q)

def bs_put_delta(S, K, T, r, sigma, q=0.0):
    """Calculate Black-Scholes put option delta."""
    return -np.exp(-q * T) * _Nmd1(S, K, T, r, sigma, q)

def bs_put_gamma(S, K, T, r, sigma, q=0.0):
    """Calculate Black-Scholes put option gamma."""
    return (np.exp(-q * T) * _phi_d1(S, K, T, r, sigma, q)) / (S * sigma * np.sqrt(T))

def bs_put_vega(S, K, T, r, sigma, q=0.0):
    """Calculate Black-Scholes put option vega."""
    return S * np.exp(-q * T) * _phi_d1(S, K, T, r, sigma, q) * np.sqrt(T)

def bs_put_rho(S, K, T, r, sigma, q=0.0):
    """Calculate Black-Scholes put option rho."""
    return -K * T * np.exp(-r * T) * _Nmd2(S, K, T, r, sigma, q)

def bs_put_theta(S, K, T, r, sigma, q=0.0):
    """Calculate Black-Scholes put option theta."""
    return (
        -S * sigma * np.exp(-q * T) * _phi_d1(S, K, T, r, sigma, q) / (2 * np.sqrt(T))
        + r * K * np.exp(-r * T) * _Nmd2(S, K, T, r, sigma, q)
        - q * S * np.exp(-q * T) * _Nd1(S, K, T, r, sigma, q)
    )


# === Forward Contracts ===
def bs_forward_price(S, K, T, r, q=0.0):
    """Calculate forward price."""
    return S * np.exp(-q * T) - K * np.exp(-r * T)

def bs_forward_delta(S, K, T, r, q=0.0):
    """Calculate forward delta."""
    return np.exp(-q * T)

def bs_forward_gamma(S, K, T, r, q=0.0):
    """Calculate forward gamma."""
    return 0.0

def bs_forward_vega(S, K, T, r, q=0.0):
    """Calculate forward vega."""
    return 0.0

def bs_forward_rho(S, K, T, r, q=0.0):
    """Calculate forward rho."""
    return K * T * np.exp(-r * T)

def bs_forward_theta(S, K, T, r, q=0.0):
    """Calculate forward theta."""
    return q * S * np.exp(-q * T) - r * K * np.exp(-r * T)


# === Binary Call Options ===
def bs_binary_call_price(S, K, T, r, sigma, q=0.0):
    """Calculate binary call option price."""
    return np.exp(-r * T) * _Nd2(S, K, T, r, sigma, q)

def bs_binary_call_delta(S, K, T, r, sigma, q=0.0):
    """Calculate binary call option delta."""
    return (np.exp(-r * T) * _phi_d2(S, K, T, r, sigma, q)) / (S * sigma * np.sqrt(T))

def bs_binary_call_gamma(S, K, T, r, sigma, q=0.0):
    """Calculate binary call option gamma."""
    d2 = _d2(S, K, T, r, sigma, q)
    return -(np.exp(-r * T) * _phi_d2(S, K, T, r, sigma, q) * d2) / (S**2 * sigma**2 * T)

def bs_binary_call_vega(S, K, T, r, sigma, q=0.0):
    """Calculate binary call option vega."""
    d2 = _d2(S, K, T, r, sigma, q)
    return -np.exp(-r * T) * _phi_d2(S, K, T, r, sigma, q) * d2 / sigma

def bs_binary_call_rho(S, K, T, r, sigma, q=0.0):
    """Calculate binary call option rho."""
    d2 = _d2(S, K, T, r, sigma, q)
    return -T * np.exp(-r * T) * stats.norm.cdf(d2) + np.exp(-r * T) * stats.norm.pdf(d2) * np.sqrt(T) / sigma

def bs_binary_call_theta(S, K, T, r, sigma, q=0.0):
    """Calculate binary call option theta."""
    d2 = _d2(S, K, T, r, sigma, q)
    return -np.exp(-r * T) * (
        -r * stats.norm.cdf(d2) + stats.norm.pdf(d2) * ((r - q - 0.5 * sigma**2) / (sigma * np.sqrt(T)) - d2 / (2 * T))
    )


# === Binary Put Options ===
def bs_binary_put_price(S, K, T, r, sigma, q=0.0):
    """Calculate binary put option price."""
    return np.exp(-r * T) * _Nmd2(S, K, T, r, sigma, q)

def bs_binary_put_delta(S, K, T, r, sigma, q=0.0):
    """Calculate binary put option delta."""
    return -(np.exp(-r * T) * _phi_d2(S, K, T, r, sigma, q)) / (S * sigma * np.sqrt(T))

def bs_binary_put_gamma(S, K, T, r, sigma, q=0.0):
    """Calculate binary put option gamma."""
    d2 = _d2(S, K, T, r, sigma, q)
    return (np.exp(-r * T) * _phi_d2(S, K, T, r, sigma, q) * d2) / (S**2 * sigma**2 * T)

def bs_binary_put_vega(S, K, T, r, sigma, q=0.0):
    """Calculate binary put option vega."""
    d2 = _d2(S, K, T, r, sigma, q)
    return np.exp(-r * T) * _phi_d2(S, K, T, r, sigma, q) * d2 / sigma

def bs_binary_put_rho(S, K, T, r, sigma, q=0.0):
    """Calculate binary put option rho."""
    d2 = _d2(S, K, T, r, sigma, q)
    return -T * np.exp(-r * T) * stats.norm.cdf(-d2) - np.exp(-r * T) * stats.norm.pdf(d2) * np.sqrt(T) / sigma

def bs_binary_put_theta(S, K, T, r, sigma, q=0.0):
    """Calculate binary put option theta."""
    d2 = _d2(S, K, T, r, sigma, q)
    return -np.exp(-r * T) * (
        r * stats.norm.cdf(-d2) + stats.norm.pdf(d2) * ((r - q - 0.5 * sigma**2) / (sigma * np.sqrt(T)) + d2 / (2 * T))
    )