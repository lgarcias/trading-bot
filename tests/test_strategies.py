import pandas as pd
import pytest
from src.strategies.cross_sma_func import cross_sma
from src.strategies.cross_ema_func import cross_ema
from src import strategies

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

def test_get_strategy_cross_sma():
    func = strategies.get_strategy('cross_sma')
    assert callable(func)
    # Minimal DataFrame for SMA
    df = pd.DataFrame({'close': [1, 2, 3, 4, 5, 6]})
    result = func(df.copy(), fast=2, slow=3)
    assert result in ("BUY", "SELL", "HOLD")

def test_get_strategy_cross_ema():
    func = strategies.get_strategy('cross_ema')
    assert callable(func)
    # Minimal DataFrame for EMA
    df = pd.DataFrame({'close': [1, 2, 3, 4, 5, 6]})
    result = func(df.copy(), fast=2, slow=3)
    assert result in ("BUY", "SELL", "HOLD")

def test_get_strategy_invalid():
    with pytest.raises(ValueError) as exc:
        strategies.get_strategy('not_a_strategy')
    assert "Unknown strategy" in str(exc.value)

# Explanation: These tests check that the strategy factory returns the correct function for known names, raises an error for unknown names, and that the returned functions are callable and produce a valid signal on minimal input.
