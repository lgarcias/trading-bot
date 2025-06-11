"""
SMA crossover trading strategy implementation.

This module provides the cross_sma function to generate trading signals based on simple moving average crossovers.
"""

import pandas_ta as ta
import logging
import math

def cross_sma(df, fast, slow):
    """
    Generate a trading signal based on SMA crossover.

    Args:
        df (pd.DataFrame): DataFrame with at least a 'close' column.
        fast (int): Fast SMA period.
        slow (int): Slow SMA period.

    Returns:
        str: 'BUY', 'SELL', or 'HOLD' depending on the crossover condition.
    """
    if 'sma_fast' not in df.columns:
        df['sma_fast'] = ta.sma(df['close'], length=fast)
    if 'sma_slow' not in df.columns:
        df['sma_slow'] = ta.sma(df['close'], length=slow)
    prev_fast = df['sma_fast'].iloc[-2]
    prev_slow = df['sma_slow'].iloc[-2]
    curr_fast = df['sma_fast'].iloc[-1]
    curr_slow = df['sma_slow'].iloc[-1]
    # Check for NaN or None
    if any(x is None or (isinstance(x, float) and math.isnan(x)) for x in [prev_fast, prev_slow, curr_fast, curr_slow]):
        return "HOLD"
    if prev_fast < prev_slow and curr_fast > curr_slow:
        logging.info("Signal: BUY (cross_sma)")
        return "BUY"
    if prev_fast > prev_slow and curr_fast < curr_slow:
        logging.info("Signal: SELL (cross_sma)")
        return "SELL"
    logging.info("Signal: HOLD (cross_sma)")
    return "HOLD"
