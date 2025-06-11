"""
Run backtest for the cross_ema strategy and save results in the strategy's data folder.

Usage:
    python backtest_cross_ema.py
"""
import sys
sys.path.append('../../')
from src.backtest import backtest_strategy

# Example parameters
symbol = 'BTC-USDT'
timeframe = '1m'
strategy_name = 'cross_ema'
input_csv = '../../data/historico.csv'
output_csv = '../../data/strategies/cross_ema/backtest_BTC-USDT_1m.csv'

backtest_strategy(strategy_name, symbol, timeframe, input_csv, output_csv)
print(f"Backtest saved to {output_csv}")
