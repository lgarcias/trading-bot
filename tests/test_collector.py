import pandas as pd
import pytest
from unittest.mock import patch, MagicMock

from src.collector import fetch_ohlcv

@pytest.fixture
def fake_ohlcv():
    # 3 velas con timestamp en ms y OHLCV dummy
    return [
        [1000, 1, 2, 0.5, 1.5, 10],
        [2000, 1.5, 2.5, 1.0, 2.0, 12],
        [3000, 2.0, 3.0, 1.5, 2.5, 15],
    ]

@patch('src.collector.ccxt.binance')
def test_fetch_ohlcv_dataframe(mock_binance, fake_ohlcv):
    # Prepara el mock de ccxt.binance()
    instance = MagicMock()
    instance.fetch_ohlcv.return_value = fake_ohlcv
    mock_binance.return_value = instance

    df = fetch_ohlcv(symbol="X/Y", timeframe="1m", limit=3)
    # Comprueba tipo y columnas
    assert isinstance(df, pd.DataFrame)
    assert list(df.columns) == ['ts', 'open', 'high', 'low', 'close', 'volume']
    # Comprueba que las timestamps se convierten a datetime
    assert pd.api.types.is_datetime64_any_dtype(df['ts'])
    # Comprueba número de filas
    assert len(df) == 3
