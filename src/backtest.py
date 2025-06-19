"""
Backtesting module for trading strategies.

This module provides a function to apply a trading strategy to historical OHLCV data and generate trading signals.

Usage (as a script):
    python -m src.backtest

Typical usage (as a module):
    from src.backtest import backtest_strategy
    result = backtest_strategy(df, strategy, fast, slow)
"""
import os
import pandas as pd
from typing import Callable, List
import logging

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
    parser.add_argument('--output-dir', type=str, default=None, help='Directorio de salida para los resultados')
    args = parser.parse_args()

    STRATEGY_NAME = args.strategy
    SYMBOL = args.symbol
    TIMEFRAME = args.timeframe
    fast = args.fast
    slow = args.slow
    # Puedes usar args.limit, args.max_position_size, args.stop_loss_pct según lo requiera tu lógica

    HIST_CSV = args.history or "data/historico.csv"
    try:
        # Cargar o descargar histórico
        if os.path.exists(HIST_CSV):
            logging.info(f"Loading historical data from {HIST_CSV}")
            df = pd.read_csv(HIST_CSV)
            if 'ts' in df.columns:
                df['ts'] = pd.to_datetime(df['ts'])
        else:
            logging.info("Downloading historical data...")
            df = fetch_ohlcv(SYMBOL, TIMEFRAME, limit=200)
            os.makedirs("data", exist_ok=True)
            df.to_csv(HIST_CSV, index=False)
            logging.info(f"Data saved to {HIST_CSV}")
        # Filtrar por fechas si se proporcionan
        if args.start_date:
            df = df[df['ts'] >= pd.to_datetime(args.start_date)]
        if args.end_date:
            df = df[df['ts'] <= pd.to_datetime(args.end_date)]
        strategy = get_strategy(STRATEGY_NAME)
        result = backtest_strategy(df, strategy, fast=fast, slow=slow)
        # === NUEVO: Directorio de salida configurable ===
        if args.output_dir:
            strategy_dir = os.path.join(args.output_dir, STRATEGY_NAME)
        else:
            strategy_dir = os.path.join('data', 'strategies', STRATEGY_NAME)
        os.makedirs(strategy_dir, exist_ok=True)
        out_name = os.path.join(strategy_dir, f"backtest_{SYMBOL.replace('/', '-')}_{TIMEFRAME}.csv")
        summary_name = out_name.replace('.csv', '_summary.json')
        # === NUEVO: Guardar resumen JSON ===
        import numpy as np
        import json
        summary = {}
        # Emparejar señales BUY/SELL para calcular trades completos
        trades_list = []
        open_trade = None
        for idx, row in result.iterrows():
            if row['signal'] == 'BUY' and open_trade is None:
                open_trade = {
                    'entry_time': str(row['ts']),
                    'entry_price': float(row['close']),
                    'entry_idx': idx
                }
            elif row['signal'] == 'SELL' and open_trade is not None:
                trade = {
                    'entry_time': open_trade['entry_time'],
                    'entry_price': open_trade['entry_price'],
                    'exit_time': str(row['ts']),
                    'exit_price': float(row['close']),
                    'profit': float(row['close']) - open_trade['entry_price']
                }
                trades_list.append(trade)
                open_trade = None
        # Si queda una operación abierta al final, la ignoramos (o podrías cerrarla al último precio)
        summary['total_trades'] = len(trades_list)
        summary['start_date'] = str(result['ts'].iloc[0]) if not result.empty else None
        summary['end_date'] = str(result['ts'].iloc[-1]) if not result.empty else None
        summary['symbol'] = SYMBOL
        summary['timeframe'] = TIMEFRAME
        summary['strategy'] = STRATEGY_NAME
        # Equity curve: acumulado de profits
        equity_curve = np.cumsum([t['profit'] for t in trades_list]).tolist() if trades_list else []
        summary['equity_curve'] = equity_curve
        # Drawdown
        if equity_curve:
            peak = np.maximum.accumulate(equity_curve)
            drawdown = (np.array(equity_curve) - peak).tolist()
            summary['drawdown_curve'] = drawdown
            summary['max_drawdown'] = float(np.min(drawdown))
        else:
            summary['drawdown_curve'] = []
            summary['max_drawdown'] = 0.0
        # Ganancia/pérdida total
        summary['total_profit'] = float(np.sum([t['profit'] for t in trades_list])) if trades_list else 0.0
        # Guardar los primeros 20 trades para tabla
        summary['trades'] = trades_list[:20]
        # Parámetros de la estrategia
        summary['strategy_params'] = {
            'fast': fast,
            'slow': slow,
            'limit': getattr(args, 'limit', None),
            'max_position_size': getattr(args, 'max_position_size', None),
            'stop_loss_pct': getattr(args, 'stop_loss_pct', None),
            'start_date': getattr(args, 'start_date', None),
            'end_date': getattr(args, 'end_date', None)
        }
    except Exception as e:
        logging.error(f"Critical error in backtest script: {e}")
        raise
    # Guardar archivos solo si todo fue exitoso (fuera del try)
    result.to_csv(out_name, index=False)
    logging.info(f"Backtest saved to {out_name}")
    with open(summary_name, 'w', encoding='utf-8') as f:
        json.dump(summary, f, ensure_ascii=False, indent=2, default=str)
    logging.info(f"Summary saved to {summary_name}")
