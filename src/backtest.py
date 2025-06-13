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
    import argparse
    from src.collector import fetch_ohlcv
    from src.strategies import get_strategy
    from src.config import SYMBOL, TIMEFRAME, STRAT_PARAMS

    parser = argparse.ArgumentParser()
    parser.add_argument('--strategy', type=str, default='cross_sma')
    parser.add_argument('--symbol', type=str, default=SYMBOL)
    parser.add_argument('--timeframe', type=str, default=TIMEFRAME)
    parser.add_argument('--history', type=str, default=None)
    parser.add_argument('--start_date', type=str, default=None)
    parser.add_argument('--end_date', type=str, default=None)
    parser.add_argument('--fast', type=int, default=STRAT_PARAMS.get('fast', 10))
    parser.add_argument('--slow', type=int, default=STRAT_PARAMS.get('slow', 50))
    parser.add_argument('--limit', type=int, default=STRAT_PARAMS.get('limit', 100))
    parser.add_argument('--max_position_size', type=float, default=STRAT_PARAMS.get('max_position_size', 0.01))
    parser.add_argument('--stop_loss_pct', type=float, default=STRAT_PARAMS.get('stop_loss_pct', 0.02))
    args = parser.parse_args()

    STRATEGY_NAME = args.strategy
    SYMBOL = args.symbol
    TIMEFRAME = args.timeframe
    fast = args.fast
    slow = args.slow
    # Puedes usar args.limit, args.max_position_size, args.stop_loss_pct según lo requiera tu lógica

    HIST_CSV = args.history or "data/historico.csv"
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
    # Filtrar por fechas si se proporcionan
    if args.start_date:
        df = df[df['ts'] >= pd.to_datetime(args.start_date)]
    if args.end_date:
        df = df[df['ts'] <= pd.to_datetime(args.end_date)]
    strategy = get_strategy(STRATEGY_NAME)
    result = backtest_strategy(df, strategy, fast=fast, slow=slow)
    print(result[['ts','close','signal']].tail(20))

    # Save backtest result with descriptive name
    strategy_dir = os.path.join('data', 'strategies', STRATEGY_NAME)
    os.makedirs(strategy_dir, exist_ok=True)
    out_name = os.path.join(strategy_dir, f"backtest_{SYMBOL.replace('/', '-')}_{TIMEFRAME}.csv")
    result.to_csv(out_name, index=False)
    print(f"Backtest saved to {out_name}")
