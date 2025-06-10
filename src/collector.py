# collector.py
import ccxt
import os
import pandas as pd
import logging

from src.config import SYMBOL, TIMEFRAME, API_KEY, API_SECRET  # asumimos que config.py expone estas variables

logging.basicConfig(
    filename='logs/bot.log',
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s'
)

def fetch_ohlcv(symbol, timeframe, limit=100):
    exchange = ccxt.binance({
        'apiKey': API_KEY,
        'secret': API_SECRET,
    })
    logging.info(f"Fetching {limit} bars for {symbol} @ {timeframe}")
    data = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
    df = pd.DataFrame(data, columns=['ts','open','high','low','close','volume'])
    df['ts'] = pd.to_datetime(df['ts'], unit='ms')
    logging.info(f"Fetched {len(df)} bars")
    return df

if __name__ == "__main__":
    # Ejecuta una prueba rápida usando la configuración
    df = fetch_ohlcv(SYMBOL, TIMEFRAME, limit=10)
    print(df)               # muestra todo el DataFrame
    # o bien:
    # print(df.tail())      # sólo las últimas filas
