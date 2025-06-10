# src/run.py

from src.collector import fetch_ohlcv
from src.config import STRAT_PARAMS, SYMBOL, TIMEFRAME
from src.strategies import get_strategy

STRATEGY_NAME = 'cross_sma'  # o 'cross_ema'

def main():
    df = fetch_ohlcv(SYMBOL, TIMEFRAME, limit=100)
    strategy = get_strategy(STRATEGY_NAME)
    sig = strategy(df,
                   fast=STRAT_PARAMS['fast'],
                   slow=STRAT_PARAMS['slow'])
    print(f"Señal actual: {sig}")
    # Aquí esperas a la fase de executor para enviar la orden

if __name__ == "__main__":
    main()
