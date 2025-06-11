import pandas as pd
import pytest
from src.strategies.cross_sma_func import cross_sma
from src.strategies.cross_ema_func import cross_ema
from src.backtest import backtest_strategy

@pytest.fixture
def sample_data():
    # Crea un DataFrame de ejemplo OHLCV
    data = [
        ["2025-06-11 13:55:00", 100, 105, 99, 104, 10],
        ["2025-06-11 13:56:00", 104, 106, 103, 105, 12],
        ["2025-06-11 13:57:00", 105, 107, 104, 106, 15],
        ["2025-06-11 13:58:00", 106, 108, 105, 107, 11],
        ["2025-06-11 13:59:00", 107, 109, 106, 108, 13],
        ["2025-06-11 14:00:00", 108, 110, 107, 109, 14],
    ]
    df = pd.DataFrame(data, columns=["ts", "open", "high", "low", "close", "volume"])
    return df

def test_backtest_strategy_cross_sma(sample_data):
    result = backtest_strategy(sample_data, cross_sma, 3, 5)
    assert "signal" in result.columns
    assert len(result) == len(sample_data)
    assert set(result['signal'].dropna().unique()).issubset({"BUY", "SELL", "HOLD"})

def test_backtest_strategy_cross_ema(sample_data):
    result = backtest_strategy(sample_data, cross_ema, 3, 5)
    assert "signal" in result.columns
    assert len(result) == len(sample_data)
    assert set(result['signal'].dropna().unique()).issubset({"BUY", "SELL", "HOLD"})
