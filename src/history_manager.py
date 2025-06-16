"""
History Manager for Crypto Bot
Manages historical data files and a global meta JSON file with min/max dates for each symbol/timeframe.
All strategies should use the shared files in /data/history/.
"""
import os
import json
from datetime import datetime
from typing import Dict, Optional

HISTORY_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'history')
META_FILE = os.path.join(HISTORY_DIR, 'history_meta.json')

def symbol_to_filename(symbol: str) -> str:
    """Convierte BTC/USDT a BTC-USDT para nombres de archivo."""
    return symbol.replace('/', '-')

class HistoryManager:
    @staticmethod
    def load_meta() -> Dict:
        if not os.path.exists(META_FILE):
            return {}
        with open(META_FILE, 'r') as f:
            return json.load(f)

    @staticmethod
    def save_meta(meta: Dict):
        with open(META_FILE, 'w') as f:
            json.dump(meta, f, indent=2)

    @staticmethod
    def update_meta(symbol: str, timeframe: str, min_date: str, max_date: str, filename: str):
        meta = HistoryManager.load_meta()
        if symbol not in meta:
            meta[symbol] = {}
        meta[symbol][timeframe] = {
            'filename': filename,
            'min_date': min_date,
            'max_date': max_date
        }
        HistoryManager.save_meta(meta)

    @staticmethod
    def remove_meta(symbol: str, timeframe: str):
        meta = HistoryManager.load_meta()
        changed = False
        if symbol in meta and timeframe in meta[symbol]:
            del meta[symbol][timeframe]
            changed = True
            if not meta[symbol]:
                del meta[symbol]
        if changed:
            HistoryManager.save_meta(meta)
        return changed

    @staticmethod
    def get_meta(symbol: str, timeframe: str) -> Optional[Dict]:
        meta = HistoryManager.load_meta()
        return meta.get(symbol, {}).get(timeframe)

    @staticmethod
    def list_all():
        """Return all meta info for all historical files."""
        return HistoryManager.load_meta()

    @staticmethod
    def get_history_file(symbol: str, timeframe: str) -> str:
        # Usa el símbolo con barra para la API, pero guion para el nombre de archivo
        return os.path.join(HISTORY_DIR, f"history_{symbol_to_filename(symbol)}_{timeframe}.csv")

    @staticmethod
    def list_history_files():
        """Return all history CSV files in the directory."""
        return [f for f in os.listdir(HISTORY_DIR) if f.startswith('history_') and f.endswith('.csv')]
