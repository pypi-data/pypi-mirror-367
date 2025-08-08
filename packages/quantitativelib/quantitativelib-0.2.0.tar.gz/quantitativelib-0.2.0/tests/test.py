from quantitativelib.stats import analyse
from quantitativelib.options import black_scholes


# Example usage of the `analyse` function
analyse(
    ticker=["AAPL", "MSFT", "GOOGL"],
    start_date="2021-01-01",
    end_date="2023-01-01",  
    overlay_price=True,
    stats=["mean", "sharpe", "cumulative"],
    round_decimals=3,
    plot_kwargs={"grid": True},
)

# Example usage of the `black_scholes` function
option_prices = black_scholes(
    option_type=['call', 'put'],
    K=150,
    S=145,
    T=1,
    r=0.01,  
    q=0.02,  
    sigma=0.2,  
    precision=4,
    show_table=True
)