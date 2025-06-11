"""
Backtesting module for trading strategies.

This module provides a function to apply a trading strategy to historical OHLCV data and generate trading signals.

Usage (as a script):
    python -m src.backtest

Typical usage (as a module):
    from src.backtest import backtest_strategy
    result = backtest_strategy(df, strategy, fast, slow)
"""
from src import monkeypatch_numpy
import os
import pandas as pd
from typing import Callable, List

def backtest_strategy(df: pd.DataFrame, strategy: Callable, fast: int, slow: int) -> pd.DataFrame:
    """
    Apply a trading strategy to a DataFrame of OHLCV data and return a DataFrame with generated signals.

    Args:
        df (pd.DataFrame): Historical OHLCV data.
        strategy (Callable): Strategy function accepting (df, fast, slow) and returning 'BUY', 'SELL', or 'HOLD'.
        fast (int): Fast period parameter for the strategy.
        slow (int): Slow period parameter for the strategy.

    Returns:
        pd.DataFrame: DataFrame with an added 'signal' column containing the generated signals.
    """
    signals: List[str] = []
    # For each point starting from the second (due to the crossover)
    for i in range(1, len(df)):
        sub_df = df.iloc[:i+1].copy()
        signal = strategy(sub_df, fast, slow)
        signals.append(signal)
    # The first value has no signal (due to lack of history)
    signals = [None] + signals
    df = df.copy()
    df['signal'] = signals
    return df

if __name__ == "__main__":
    import sys
    from src.collector import fetch_ohlcv
    from src.strategies import get_strategy
    from src.config import SYMBOL, TIMEFRAME, STRAT_PARAMS

    HIST_CSV = "data/historico.csv"
    STRATEGY_NAME = 'cross_sma'  # Change this to select the strategy
    fast = STRAT_PARAMS['fast']
    slow = STRAT_PARAMS['slow']

    if os.path.exists(HIST_CSV):
        print(f"Loading historical data from {HIST_CSV}")
        df = pd.read_csv(HIST_CSV)
        if 'ts' in df.columns:
            df['ts'] = pd.to_datetime(df['ts'])
    else:
        print("Downloading historical data...")
        df = fetch_ohlcv(SYMBOL, TIMEFRAME, limit=200)
        os.makedirs("data", exist_ok=True)
        df.to_csv(HIST_CSV, index=False)
        print(f"Data saved to {HIST_CSV}")
    strategy = get_strategy(STRATEGY_NAME)
    result = backtest_strategy(df, strategy, fast=fast, slow=slow)
    print(result[['ts','close','signal']].tail(20))

    # Save backtest result with descriptive name
    out_name = f"data/backtest_{STRATEGY_NAME}_{SYMBOL.replace('/', '-')}_{TIMEFRAME}.csv"
    result.to_csv(out_name, index=False)
    print(f"Backtest saved to {out_name}")
