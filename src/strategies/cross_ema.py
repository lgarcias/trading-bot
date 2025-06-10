import pandas_ta as ta
import logging

def cross_ema(df, fast, slow):
    if 'ema_fast' not in df.columns:
        df['ema_fast'] = ta.ema(df['close'], length=fast)
    if 'ema_slow' not in df.columns:
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
