"""
Move backtest data files for a given strategy to its dedicated folder under data/strategies/<strategy>/.

This script can be used as a module or as a standalone script:
    python move_strategy_data.py <strategy> <symbol> <timeframe>

Example:
    python move_strategy_data.py cross_sma BTC-USDT 1m
"""
import shutil
import os
import sys

def move_strategy_data(strategy_name, symbol, timeframe, base_dir="data"):
    """
    Move the backtest CSV file for a strategy to its dedicated folder under base_dir/strategies/<strategy>/.

    Args:
        strategy_name (str): Name of the strategy (e.g., 'cross_sma')
        symbol (str): Trading symbol (e.g., 'BTC-USDT')
        timeframe (str): Timeframe string (e.g., '1m')
        base_dir (str): Base directory for data (default: 'data')

    Returns:
        bool: True if the file was moved, False if the source file was not found.
    """
    src = os.path.join(base_dir, f"backtest_{strategy_name}_{symbol}_{timeframe}.csv")
    dst_dir = os.path.join(base_dir, "strategies", strategy_name)
    dst = os.path.join(dst_dir, f"backtest_{symbol}_{timeframe}.csv")
    os.makedirs(dst_dir, exist_ok=True)
    if os.path.exists(src):
        shutil.move(src, dst)
        print(f"Moved file to {dst}")
        return True
    else:
        print(f"Source file not found: {src}")
        return False

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Move backtest data to strategy folder.")
    parser.add_argument("strategy", help="Strategy name")
    parser.add_argument("symbol", help="Symbol")
    parser.add_argument("timeframe", help="Timeframe")
    parser.add_argument("--base-dir", default="data", help="Base directory for data (default: 'data')")
    args = parser.parse_args()
    move_strategy_data(args.strategy, args.symbol, args.timeframe, base_dir=args.base_dir)
