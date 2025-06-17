"""
Strategy loader and registry module.

This module provides utilities to dynamically load and manage trading strategies.
"""

# If pandas_ta is used, ensure numpy.NaN is available for compatibility
# This monkeypatch is required because some pandas_ta indicators expect np.NaN to exist
import pandas_ta as ta
import logging
import src.monkeypatch_numpy  # Ensures np.NaN exists if pandas_ta is used

# Strategy 1: SMA Crossover (cross_sma)
def cross_sma(df, fast, slow):
    df['sma_fast'] = ta.sma(df['close'], length=fast)
    df['sma_slow'] = ta.sma(df['close'], length=slow)
    prev_fast = df['sma_fast'].iloc[-2]
    prev_slow = df['sma_slow'].iloc[-2]
    curr_fast = df['sma_fast'].iloc[-1]
    curr_slow = df['sma_slow'].iloc[-1]
    if prev_fast < prev_slow and curr_fast > curr_slow:
        logging.info("Signal: BUY (cross_sma)")
        return "BUY"
    if prev_fast > prev_slow and curr_fast < curr_slow:
        logging.info("Signal: SELL (cross_sma)")
        return "SELL"
    logging.info("Signal: HOLD (cross_sma)")
    return "HOLD"

# Strategy 2: EMA Crossover (cross_ema)
def cross_ema(df, fast, slow):
    df['ema_fast'] = ta.ema(df['close'], length=fast)
    df['ema_slow'] = ta.ema(df['close'], length=slow)
    prev_fast = df['ema_fast'].iloc[-2]
    prev_slow = df['ema_slow'].iloc[-2]
    curr_fast = df['ema_fast'].iloc[-1]
    curr_slow = df['ema_slow'].iloc[-1]
    if prev_fast < prev_slow and curr_fast > curr_slow:
        logging.info("Signal: BUY (cross_ema)")
        return "BUY"
    if prev_fast > prev_slow and curr_fast < curr_slow:
        logging.info("Signal: SELL (cross_ema)")
        return "SELL"
    logging.info("Signal: HOLD (cross_ema)")
    return "HOLD"

# Strategy factory
def get_strategy(name):
    if name == 'cross_sma':
        return cross_sma
    elif name == 'cross_ema':
        return cross_ema
    else:
        # Always raise the error in English for test compatibility
        raise ValueError(f"Unknown strategy: {name}")
