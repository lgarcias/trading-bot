from src import monkeypatch_numpy
import pandas as pd
import pytest
from src.strategies.cross_sma import cross_sma

def get_df():
    return pd.DataFrame({'close': [100, 102, 104, 106, 108, 110]})

def test_cross_sma_buy():
    df = get_df()
    df['sma_fast'] = [1, 1, 1, 1, 4, 6]
    df['sma_slow'] = [1, 1, 1, 1, 5, 5]
    assert cross_sma(df, fast=3, slow=5) == "BUY"

def test_cross_sma_sell():
    df = get_df()
    df['sma_fast'] = [1, 1, 1, 1, 6, 4]
    df['sma_slow'] = [1, 1, 1, 1, 5, 5]
    assert cross_sma(df, fast=3, slow=5) == "SELL"

def test_cross_sma_hold():
    df = get_df()
    df['sma_fast'] = [1, 1, 1, 1, 5, 5]
    df['sma_slow'] = [1, 1, 1, 1, 5, 5]
    assert cross_sma(df, fast=3, slow=5) == "HOLD"
