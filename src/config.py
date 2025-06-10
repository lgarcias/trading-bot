# src/config.py
import os, yaml
from dotenv import load_dotenv

# 1) Cargar secretos
load_dotenv()
API_KEY    = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")

# 2) Cargar configuración general
with open("config.yaml", "r", encoding="utf-8") as f:
    cfg = yaml.safe_load(f)

# Ahora puedes usar:
EXCHANGE = cfg["exchange"]["name"]
SYMBOL   = cfg["exchange"]["symbol"]
TIMEFRAME= cfg["exchange"]["timeframe"]

STRAT_TYPE   = cfg["strategy"]["type"]
STRAT_PARAMS = cfg["strategy"]["params"]
LIMIT = STRAT_PARAMS.get("limit", 50)

RISK_PARAMS  = cfg["risk"]
