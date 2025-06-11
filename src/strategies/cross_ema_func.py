"""
EMA crossover trading strategy implementation.

This module provides the cross_ema function to generate trading signals based on exponential moving average crossovers.
"""

import pandas_ta as ta
import logging
import math

def cross_ema(df, fast, slow):
    """
    Generate a trading signal based on EMA crossover.

    Args:
        df (pd.DataFrame): DataFrame with at least a 'close' column.
        fast (int): Fast EMA period.
        slow (int): Slow EMA period.

    Returns:
        str: 'BUY', 'SELL', or 'HOLD' depending on the crossover condition.
    """
    if 'ema_fast' not in df.columns:
        df['ema_fast'] = ta.ema(df['close'], length=fast)
    if 'ema_slow' not in df.columns:
        df['ema_slow'] = ta.ema(df['close'], length=slow)
    prev_fast = df['ema_fast'].iloc[-2]
    prev_slow = df['ema_slow'].iloc[-2]
    curr_fast = df['ema_fast'].iloc[-1]
    curr_slow = df['ema_slow'].iloc[-1]
    # Check for NaN or None
    if any(x is None or (isinstance(x, float) and math.isnan(x)) for x in [prev_fast, prev_slow, curr_fast, curr_slow]):
        return "HOLD"
    if prev_fast < prev_slow and curr_fast > curr_slow:
        logging.info("Signal: BUY (cross_ema)")
        return "BUY"
    if prev_fast > prev_slow and curr_fast < curr_slow:
        logging.info("Signal: SELL (cross_ema)")
        return "SELL"
    logging.info("Signal: HOLD (cross_ema)")
    return "HOLD"
