"""
Historical OHLCV data collector module.

This module provides functions to fetch and save historical OHLCV data for backtesting and analysis.
"""

import ccxt
import os
import pandas as pd
import logging

from src.config import SYMBOL, TIMEFRAME, API_KEY, API_SECRET  # we assume that config.py exposes these variables

logging.basicConfig(
    filename='logs/bot.log',
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s'
)

def fetch_ohlcv(symbol, timeframe, limit=100):
    """Fetch historical OHLCV data from the exchange."""
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

def download_ohlcv_to_csv(symbol, timeframe, limit, filename):
    """
    Download historical OHLCV data and save it to a CSV file.

    Args:
        symbol (str): Trading symbol (e.g., 'BTC-USDT')
        timeframe (str): Timeframe string (e.g., '1m')
        limit (int): Number of data points to download
        filename (str): Output CSV file path
    """
    df = fetch_ohlcv(symbol, timeframe, limit)
    df.to_csv(filename, index=False)
    print(f"Data saved to {filename}")

if __name__ == "__main__":
    # Run a quick test using the configuration
    df = fetch_ohlcv(SYMBOL, TIMEFRAME, limit=10)
    print(df)               # show the entire DataFrame
    # or:
    # print(df.tail())      # only the last few rows
    # Example download for backtesting
    # download_ohlcv_to_csv(SYMBOL, TIMEFRAME, 1000, "data/historical.csv")
