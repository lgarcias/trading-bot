"""
Historical OHLCV data collector module.

This module provides functions to fetch and save historical OHLCV data for backtesting and analysis.
"""

import ccxt
import os
import pandas as pd
import logging
import requests

from src.config import SYMBOL, TIMEFRAME, API_KEY, API_SECRET  # we assume that config.py exposes these variables

logging.basicConfig(
    filename='logs/bot.log',
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s'
)

def get_binance_server_time():
    url = "https://api.binance.com/api/v3/time"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        return response.json()["serverTime"]
    except Exception as e:
        logging.warning(f"Could not fetch Binance server time: {e}")
        return None


def fetch_ohlcv(symbol, timeframe, limit=100, since=None):
    """Fetch historical OHLCV data from the exchange with pagination, adjusting for server time."""
    exchange = ccxt.binance({
        'apiKey': API_KEY,
        'secret': API_SECRET,
        'enableRateLimit': True,
        'options': {'adjustForTimeDifference': True}
    })
    # Ajuste de desfase de reloj
    server_time = get_binance_server_time()
    local_time = int(pd.Timestamp.utcnow().timestamp() * 1000)
    time_offset = 0
    if server_time:
        time_offset = server_time - local_time
        logging.info(f"Binance time offset: {time_offset} ms")
    all_data = []
    max_per_call = exchange.rateLimit if hasattr(exchange, 'rateLimit') else 1000
    max_per_call = 1000  # Binance max
    fetched = 0
    since_ms = int(since.timestamp() * 1000) if since else None
    if since_ms is not None:
        since_ms += time_offset
    while fetched < limit:
        fetch_limit = min(max_per_call, limit - fetched)
        data = exchange.fetch_ohlcv(symbol, timeframe=timeframe, since=since_ms, limit=fetch_limit)
        if not data:
            break
        all_data.extend(data)
        fetched += len(data)
        if len(data) < fetch_limit:
            break
        since_ms = data[-1][0] + 1  # siguiente vela
    df = pd.DataFrame(all_data, columns=['ts','open','high','low','close','volume'])
    df['ts'] = pd.to_datetime(df['ts'], unit='ms')
    logging.info(f"Fetched {len(df)} bars (paginated)")
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
