import os
import pandas as pd
import pytest
from src.move_strategy_data import move_strategy_data

def setup_csv(path):
    df = pd.DataFrame({
        'ts': ['2025-06-11 13:55:00'],
        'open': [100], 'high': [105], 'low': [99], 'close': [104], 'volume': [10], 'signal': ['BUY']
    })
    df.to_csv(path, index=False)

@pytest.mark.parametrize("strategy,symbol,timeframe", [
    ("cross_sma", "BTC-USDT", "1m"),
    ("cross_ema", "BTC-USDT", "1m"),
])
def test_move_strategy_data(tmp_path, strategy, symbol, timeframe):
    base_dir = tmp_path
    src = base_dir / f"backtest_{strategy}_{symbol}_{timeframe}.csv"
    dst_dir = base_dir / f"strategies/{strategy}"
    dst = dst_dir / f"backtest_{symbol}_{timeframe}.csv"
    os.makedirs(dst_dir, exist_ok=True)
    setup_csv(src)
    assert move_strategy_data(strategy, symbol, timeframe, base_dir=str(base_dir)) is True
    assert os.path.exists(dst)
    df = pd.read_csv(dst)
    assert 'signal' in df.columns
