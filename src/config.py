"""
Configuration module for trading bot.

This module defines global configuration variables for symbols, timeframes, and strategy parameters.
"""

# src/config.py
import os, yaml
from dotenv import load_dotenv

# 1) Load secrets
load_dotenv()
API_KEY    = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")

# 2) Load general configuration
with open("config.yaml", "r", encoding="utf-8") as f:
    cfg = yaml.safe_load(f)

# Now you can use:
EXCHANGE = cfg["exchange"]["name"]
SYMBOL   = cfg["exchange"]["symbol"]
TIMEFRAME= cfg["exchange"]["timeframe"]

STRAT_TYPE   = cfg["strategy"]["type"]
STRAT_PARAMS = cfg["strategy"]["params"]
LIMIT = STRAT_PARAMS.get("limit", 50)

RISK_PARAMS  = cfg["risk"]
