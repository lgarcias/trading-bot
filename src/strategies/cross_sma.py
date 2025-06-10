import pandas_ta as ta
import logging

def cross_sma(df, fast, slow):
    if 'sma_fast' not in df.columns:
        df['sma_fast'] = ta.sma(df['close'], length=fast)
    if 'sma_slow' not in df.columns:
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
