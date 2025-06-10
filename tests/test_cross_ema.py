from src import monkeypatch_numpy
import pandas as pd
import pytest
from src.strategies.cross_ema import cross_ema

def get_df():
    return pd.DataFrame({'close': [100, 102, 104, 106, 108, 110]})

def test_cross_ema_buy():
    df = get_df()
    df['ema_fast'] = [1, 1, 1, 1, 4, 6]
    df['ema_slow'] = [1, 1, 1, 1, 5, 5]
    assert cross_ema(df, fast=3, slow=5) == "BUY"

def test_cross_ema_sell():
    df = get_df()
    df['ema_fast'] = [1, 1, 1, 1, 6, 4]
    df['ema_slow'] = [1, 1, 1, 1, 5, 5]
    assert cross_ema(df, fast=3, slow=5) == "SELL"

def test_cross_ema_hold():
    df = get_df()
    df['ema_fast'] = [1, 1, 1, 1, 5, 5]
    df['ema_slow'] = [1, 1, 1, 1, 5, 5]
    assert cross_ema(df, fast=3, slow=5) == "HOLD"
