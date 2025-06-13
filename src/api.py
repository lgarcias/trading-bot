"""
FastAPI backend to trigger backtesting for a selected strategy.
"""
from fastapi import FastAPI, Query, HTTPException, Body
from pydantic import BaseModel
import subprocess
import os
import sys
from typing import Optional
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
from src.collector import download_ohlcv_to_csv
import yaml

app = FastAPI(title="Crypto Bot Backtest API")

# Habilitar CORS para permitir peticiones desde el frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exponer la carpeta data/ como archivos estáticos para el frontend
app.mount("/data", StaticFiles(directory="data"), name="data")

HISTORY_DIR = os.path.join("data", "history")
os.makedirs(HISTORY_DIR, exist_ok=True)

def get_history_filename(symbol, timeframe, start_date, end_date):
    # Formato: history_SYMBOL_TIMEFRAME_STARTDATE_ENDDATE.csv
    import re
    s = symbol.replace('/', '-')
    def clean_date(dt):
        # Quitar espacios, dos puntos y otros caracteres no válidos
        return re.sub(r'[^0-9A-Za-z_-]', '', dt.replace(' ', '_'))
    start = clean_date(start_date.split('T')[0] if 'T' in start_date else start_date)
    end = clean_date(end_date.split('T')[0] if 'T' in end_date else end_date)
    return os.path.join(HISTORY_DIR, f"history_{s}_{timeframe}_{start}_{end}.csv")

def normalize_symbol(symbol: str) -> str:
    """Convierte BTC-USDT a BTC/USDT para CCXT."""
    return symbol.replace('-', '/')

class BacktestRequest(BaseModel):
    strategy: str
    symbol: str
    timeframe: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    # Optional: add more params as needed

def load_strategy_config(strategy: str):
    config_path = os.path.join("src", "strategies", strategy, "config.yaml")
    if not os.path.exists(config_path):
        return None
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

@app.post("/backtest/")
def run_backtest(req: BacktestRequest):
    """
    Run the backtest for the given strategy, symbol, timeframe, and date range.
    """
    symbol = req.symbol
    timeframe = req.timeframe
    start_date = getattr(req, 'start_date', None)
    end_date = getattr(req, 'end_date', None)
    # Validar config de la estrategia
    config = load_strategy_config(req.strategy)
    extra_args = []
    if config:
        allowed = config.get('allowed_symbols', [])
        if allowed and symbol not in allowed:
            return {"success": False, "error": f"Symbol {symbol} not allowed for strategy {req.strategy}"}
        ex = config.get('exchange', {})
        min_date = ex.get('start_date')
        max_date = ex.get('end_date')
        # Parsear fechas a datetime.date si es necesario
        from datetime import datetime
        def parse_date(d):
            if isinstance(d, str):
                try:
                    return datetime.strptime(d[:10], "%Y-%m-%d").date()
                except Exception:
                    return d
            return d
        start_date_dt = parse_date(start_date)
        end_date_dt = parse_date(end_date)
        min_date_dt = parse_date(min_date)
        max_date_dt = parse_date(max_date)
        if min_date and start_date and start_date_dt < min_date_dt:
            return {"success": False, "error": f"Start date {start_date} is before allowed range ({min_date})"}
        if max_date and end_date and end_date_dt > max_date_dt:
            return {"success": False, "error": f"End date {end_date} is after allowed range ({max_date})"}
        # Usar parámetros de la estrategia
        strat_params = config.get('strategy', {}).get('params', {})
        for k, v in strat_params.items():
            extra_args += [f"--{k}", str(v)]
        # Usar parámetros de risk si se usan en el backtest
        risk_params = config.get('risk', {})
        for k, v in risk_params.items():
            extra_args += [f"--{k}", str(v)]
    if not (start_date and end_date):
        return {"success": False, "error": "Start and end date required"}
    hist_file = get_history_filename(symbol, timeframe, start_date, end_date)
    if not os.path.exists(hist_file):
        return {"success": False, "error": f"No historical data for that period: {hist_file}"}
    # Llamar al backtest con el fichero histórico correcto y los parámetros
    cmd = [
        sys.executable, "-m", "src.backtest",
        "--strategy", req.strategy,
        "--symbol", symbol,
        "--timeframe", timeframe,
        "--history", hist_file
    ] + extra_args
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        out_path = os.path.join(
            "data", "strategies", req.strategy,
            f"backtest_{symbol}_{timeframe}.csv"
        )
        # Refuerzo: comprobar existencia con rutas absolutas y tolerancia a mayúsculas/minúsculas
        import glob
        abs_out_path = os.path.abspath(out_path)
        if os.path.exists(out_path) or os.path.exists(abs_out_path):
            return {"success": True, "result_file": out_path, "stdout": result.stdout}
        # Buscar por patrón si hay problemas de nombre
        pattern = os.path.join("data", "strategies", req.strategy, f"backtest_{symbol.replace('/', '-')}*{timeframe}.csv")
        matches = glob.glob(pattern)
        if matches:
            return {"success": True, "result_file": matches[0], "stdout": result.stdout}
        return {"success": False, "error": "Backtest completed but result file not found.", "stdout": result.stdout}
    except subprocess.CalledProcessError as e:
        return {"success": False, "error": str(e), "stdout": e.stdout, "stderr": e.stderr}

@app.post("/download_history/")
def download_history(
    req: BacktestRequest = Body(...)
):
    """
    Download historical data for the given symbol, timeframe, and date range.
    """
    symbol = normalize_symbol(req.symbol)
    timeframe = req.timeframe
    start_date = getattr(req, 'start_date', None)
    end_date = getattr(req, 'end_date', None)
    if not (start_date and end_date):
        return {"success": False, "error": "Start and end date required"}
    hist_file = get_history_filename(req.symbol, timeframe, start_date, end_date)
    # Aquí deberías calcular el número de velas (limit) según el timeframe y el rango de fechas
    # Por simplicidad, ponemos un límite fijo (ejemplo: 1000)
    limit = 1000
    try:
        download_ohlcv_to_csv(symbol, timeframe, limit, hist_file)
        if os.path.exists(hist_file):
            return {"success": True, "history_file": hist_file}
        else:
            return {"success": False, "error": "Download completed but file not found."}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/ping")
def ping():
    return {"status": "ok"}

@app.get("/summary/{strategy}")
def summary_generic(
    strategy: str,
    symbol: str = Query('BTC-USDT'),
    timeframe: str = Query('1m'),
    start_date: str = Query(None, description="Fecha de inicio (YYYY-MM-DD HH:MM:SS)"),
    end_date: str = Query(None, description="Fecha de fin (YYYY-MM-DD HH:MM:SS)")
):
    """
    Generic summary endpoint for any strategy. Permite filtrar por rango de fechas.
    """
    # Construir ruta del archivo de backtest
    file = os.path.join("data", "strategies", strategy, f"backtest_{symbol}_{timeframe}.csv")
    if not os.path.exists(file):
        raise HTTPException(status_code=404, detail=f"Backtest file not found: {file}")
    df = pd.read_csv(file)
    if 'ts' in df.columns:
        df['ts'] = pd.to_datetime(df['ts'])
    # Filtrado por fechas si se especifica
    if start_date:
        df = df[df['ts'] >= pd.to_datetime(start_date)]
    if end_date:
        df = df[df['ts'] <= pd.to_datetime(end_date)]
    trades = []
    position = None
    entry_price = 0
    for _, row in df.iterrows():
        signal = str(row['signal']).strip()
        price = row['close']
        if signal == 'BUY' and position is None:
            position = 'LONG'
            entry_price = price
            entry_time = row['ts']
        elif signal == 'SELL' and position == 'LONG':
            exit_price = price
            exit_time = row['ts']
            profit = exit_price - entry_price
            trades.append({
                'entry_time': entry_time,
                'entry_price': entry_price,
                'exit_time': exit_time,
                'exit_price': exit_price,
                'profit': profit
            })
            position = None
    # If the position is still open at the end, close it at the last price
    if position == 'LONG' and not df.empty:
        df_last = df.iloc[-1]
        trades.append({
            'entry_time': entry_time,
            'entry_price': entry_price,
            'exit_time': df_last['ts'],
            'exit_price': df_last['close'],
            'profit': df_last['close'] - entry_price
        })
    n_trades = len(trades)
    total_profit = sum(t['profit'] for t in trades) if n_trades > 0 else 0
    win_trades = [t for t in trades if t['profit'] > 0]
    loss_trades = [t for t in trades if t['profit'] <= 0]
    win_rate = len(win_trades) / n_trades * 100 if n_trades > 0 else 0
    avg_profit = total_profit / n_trades if n_trades > 0 else 0
    # Equity curve and drawdown
    if n_trades > 0:
        equity = [0]
        for t in trades:
            equity.append(equity[-1] + t['profit'])
        equity = equity[1:]
        peak = [max(equity[:i+1]) for i in range(len(equity))]
        drawdown = [e - p for e, p in zip(equity, peak)]
        max_drawdown = min(drawdown)
    else:
        equity = []
        drawdown = []
        max_drawdown = 0
    return {
        'total_trades': n_trades,
        'total_profit': total_profit,
        'winning_trades': len(win_trades),
        'losing_trades': len(loss_trades),
        'win_rate': win_rate,
        'avg_profit': avg_profit,
        'max_drawdown': max_drawdown,
        'trades': trades,
        'equity_curve': equity,
        'drawdown_curve': drawdown
    }
