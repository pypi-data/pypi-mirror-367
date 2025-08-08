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

# === Stochastic Functions ===
# General-purpose numerical SDE solvers

def euler_maruyama(mu, sigma, X0, T, N, dW=None):
    dt = T / N
    t = np.linspace(0, T, N + 1)
    X = np.zeros(N + 1)
    X[0] = X0
    if dW is None:
        dW = np.random.normal(0, np.sqrt(dt), size=N)
    for i in range(N):
        X[i + 1] = X[i] + mu(t[i], X[i]) * dt + sigma(t[i], X[i]) * dW[i]
    return t, X

def milstein(mu, sigma, sigma_dx, X0, T, N, dW=None):
    dt = T / N
    t = np.linspace(0, T, N + 1)
    X = np.zeros(N + 1)
    X[0] = X0
    if dW is None:
        dW = np.random.normal(0, np.sqrt(dt), size=N)
    for i in range(N):
        X[i + 1] = (
            X[i]
            + mu(t[i], X[i]) * dt
            + sigma(t[i], X[i]) * dW[i]
            + 0.5 * sigma(t[i], X[i]) * sigma_dx(t[i], X[i]) * (dW[i]**2 - dt)
        )
    return t, X

# Model-specific simulators using the above schemes 

def simulate_gbm(S0, mu, sigma, T, N, method="euler"):
    def drift(t, S): return mu * S
    def diffusion(t, S): return sigma * S
    def diffusion_dx(t, S): return sigma

    if method == "euler":
        return euler_maruyama(drift, diffusion, S0, T, N)
    elif method == "milstein":
        return milstein(drift, diffusion, diffusion_dx, S0, T, N)
    else:
        raise ValueError("Unknown method: use 'euler' or 'milstein'")

def simulate_cir(X0, kappa, theta, sigma, T, N, method="euler"):
    def drift(t, X): return kappa * (theta - X)
    def diffusion(t, X): return sigma * np.sqrt(max(X, 0))
    def diffusion_dx(t, X): return 0.5 * sigma / np.sqrt(max(X, 1e-8))

    if method == "euler":
        return euler_maruyama(drift, diffusion, X0, T, N)
    elif method == "milstein":
        return milstein(drift, diffusion, diffusion_dx, X0, T, N)
    else:
        raise ValueError("Unknown method: use 'euler' or 'milstein'")

def simulate_ou(X0, mu, theta, sigma, T, N, method="euler"):
    def drift(t, X): return mu * (theta - X)
    def diffusion(t, X): return sigma
    def diffusion_dx(t, X): return 0.0

    if method == "euler":
        return euler_maruyama(drift, diffusion, X0, T, N)
    elif method == "milstein":
        return milstein(drift, diffusion, diffusion_dx, X0, T, N)
    else:
        raise ValueError("Unknown method: use 'euler' or 'milstein'")

def simulate_heston(S0, V0, mu, kappa, theta, xi, rho, T, N):
    dt = T / N
    t = np.linspace(0, T, N + 1)
    S = np.zeros(N + 1)
    V = np.zeros(N + 1)
    S[0], V[0] = S0, V0

    for i in range(N):
        Z1 = np.random.normal()
        Z2 = np.random.normal()
        dW_v = np.sqrt(dt) * Z1
        dW_s = np.sqrt(dt) * (rho * Z1 + np.sqrt(1 - rho**2) * Z2)

        V[i + 1] = V[i] + kappa * (theta - V[i]) * dt + xi * np.sqrt(max(V[i], 0)) * dW_v
        S[i + 1] = S[i] + mu * S[i] * dt + np.sqrt(max(V[i], 0)) * S[i] * dW_s

    return t, S, V

def simulate_merton_jump(S0, mu, sigma, lambd, m, v, T, N):
    dt = T / N
    t = np.linspace(0, T, N + 1)
    S = np.zeros(N + 1)
    S[0] = S0

    for i in range(N):
        dW = np.random.normal(0, np.sqrt(dt))
        J = np.random.poisson(lambd * dt)
        jump = np.sum(np.random.normal(m, np.sqrt(v), J)) if J > 0 else 0
        S[i + 1] = S[i] * np.exp((mu - 0.5 * sigma**2) * dt + sigma * dW + jump)

    return t, S

