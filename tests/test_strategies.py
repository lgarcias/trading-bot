import pandas as pd
import pytest
from src.strategies.cross_sma_func import cross_sma
from src.strategies.cross_ema_func import cross_ema

def test_cross_sma_buy():
    df = pd.DataFrame({'close': [100, 102, 104, 106, 108, 110]})
    df['sma_fast'] = [1, 1, 1, 1, 4, 6]
    df['sma_slow'] = [1, 1, 1, 1, 5, 5]
    assert cross_sma(df, fast=3, slow=5) == "BUY"

def test_cross_sma_sell():
    df = pd.DataFrame({'close': [100, 102, 104, 106, 108, 110]})
    df['sma_fast'] = [1, 1, 1, 1, 6, 4]
    df['sma_slow'] = [1, 1, 1, 1, 5, 5]
    assert cross_sma(df, fast=3, slow=5) == "SELL"

def test_cross_sma_hold():
    df = pd.DataFrame({'close': [100, 102, 104, 106, 108, 110]})
    df['sma_fast'] = [1, 1, 1, 1, 5, 5]
    df['sma_slow'] = [1, 1, 1, 1, 5, 5]
    assert cross_sma(df, fast=3, slow=5) == "HOLD"

def test_cross_ema_buy():
    df = pd.DataFrame({'close': [100, 102, 104, 106, 108, 110]})
    df['ema_fast'] = [1, 1, 1, 1, 4, 6]
    df['ema_slow'] = [1, 1, 1, 1, 5, 5]
    assert cross_ema(df, fast=3, slow=5) == "BUY"

def test_cross_ema_sell():
    df = pd.DataFrame({'close': [100, 102, 104, 106, 108, 110]})
    df['ema_fast'] = [1, 1, 1, 1, 6, 4]
    df['ema_slow'] = [1, 1, 1, 1, 5, 5]
    assert cross_ema(df, fast=3, slow=5) == "SELL"

def test_cross_ema_hold():
    df = pd.DataFrame({'close': [100, 102, 104, 106, 108, 110]})
    df['ema_fast'] = [1, 1, 1, 1, 5, 5]
    df['ema_slow'] = [1, 1, 1, 1, 5, 5]
    assert cross_ema(df, fast=3, slow=5) == "HOLD"
