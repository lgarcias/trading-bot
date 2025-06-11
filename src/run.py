"""
Main entry point for running the trading bot.

This script initializes and starts the trading bot using the configured strategies and parameters.
"""

from src.collector import fetch_ohlcv
from src.config import STRAT_PARAMS, SYMBOL, TIMEFRAME
from src.strategies import get_strategy

STRATEGY_NAME = 'cross_sma'  # or 'cross_ema'

def main():
    df = fetch_ohlcv(SYMBOL, TIMEFRAME, limit=100)
    strategy = get_strategy(STRATEGY_NAME)
    sig = strategy(df,
                   fast=STRAT_PARAMS['fast'],
                   slow=STRAT_PARAMS['slow'])
    print(f"Current signal: {sig}")
    # Here you wait for the executor phase to send the order

if __name__ == "__main__":
    main()
