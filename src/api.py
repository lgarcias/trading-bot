"""
FastAPI backend to trigger backtesting for a selected strategy.
"""
from fastapi import FastAPI, Query, HTTPException, Body, Request
from pydantic import BaseModel
import subprocess
import os
import sys
from typing import Optional
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
from src.collector import download_ohlcv_to_csv, fetch_ohlcv
import yaml
from datetime import datetime, timedelta
import json
from src.history_manager import HistoryManager

app = FastAPI(title="Crypto Bot Backtest API")

# Enable CORS to allow requests from the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Expose the data/ folder as static files for the frontend (optional, can be removed)
app.mount("/data", StaticFiles(directory="data"), name="data")

HISTORY_DIR = os.path.join("data", "history")
os.makedirs(HISTORY_DIR, exist_ok=True)

def get_history_filename(symbol, timeframe):
    s = symbol.replace('/', '-')
    return os.path.join(HISTORY_DIR, f"history_{s}_{timeframe}.csv")

def get_history_meta_filename(symbol, timeframe):
    s = symbol.replace('/', '-')
    return os.path.join(HISTORY_DIR, f"history_{s}_{timeframe}.meta.json")

def normalize_symbol(symbol: str) -> str:
    """No longer needed, symbols are now always with slash."""
    return symbol

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
    # Validate config of the strategy
    config = load_strategy_config(req.strategy)
    extra_args = []
    if config:
        allowed = config.get('allowed_symbols', [])
        if allowed and symbol not in allowed:
            return {"success": False, "error": f"Symbol {symbol} not allowed for strategy {req.strategy}"}
        # Remove min_date and max_date validation from config.yaml
        # Use strategy parameters
        strat_params = config.get('strategy', {}).get('params', {})
        for k, v in strat_params.items():
            extra_args += [f"--{k}", str(v)]
        # Use risk parameters if they are used in the backtest
        risk_params = config.get('risk', {})
        for k, v in risk_params.items():
            extra_args += [f"--{k}", str(v)]
    if not (start_date and end_date):
        return {"success": False, "error": "Start and end date required"}
    hist_file = get_history_filename(symbol, timeframe)
    meta_file = get_history_meta_filename(symbol, timeframe)
    if not os.path.exists(hist_file) or not os.path.exists(meta_file):
        return {"success": False, "error": f"No historical data for that period: {hist_file}"}
    # Validate that the requested range is covered by the local history (according to meta.json)
    try:
        with open(meta_file, 'r', encoding='utf-8') as f:
            meta = json.load(f)
        min_hist = meta.get('start_date')
        max_hist = meta.get('end_date')
        req_start = start_date[:10]
        req_end = end_date[:10]
        if req_start < min_hist or req_end > max_hist:
            return {"success": False, "error": f"Requested range {req_start} to {req_end} is outside local history range ({min_hist} to {max_hist})"}
    except Exception as e:
        return {"success": False, "error": f"Error reading meta file: {e}"}
    # Call the backtest with the correct historical file and parameters
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
        # Reinforcement: check existence with absolute paths and case insensitivity
        import glob
        abs_out_path = os.path.abspath(out_path)
        if os.path.exists(out_path) or os.path.exists(abs_out_path):
            return {"success": True, "result_file": out_path, "stdout": result.stdout}
        # Search by pattern if there are naming issues
        pattern = os.path.join("data", "strategies", req.strategy, f"backtest_{symbol.replace('/', '-')}*{timeframe}.csv")
        matches = glob.glob(pattern)
        if matches:
            return {"success": True, "result_file": matches[0], "stdout": result.stdout}
        return {"success": False, "error": "Backtest completed but result file not found.", "stdout": result.stdout}
    except subprocess.CalledProcessError as e:
        return {"success": False, "error": str(e), "stdout": e.stdout, "stderr": e.stderr}

@app.get("/history/list")
def list_history():
    """List all available historical files and their date ranges."""
    return HistoryManager.list_all()

@app.get("/history/meta")
def get_history_meta():
    """Return the full meta JSON for all historical files."""
    return HistoryManager.list_all()

@app.delete("/history/{symbol:path}/{timeframe}")
def delete_history(symbol: str, timeframe: str):
    """Delete a historical file and update the meta JSON."""
    filename = HistoryManager.get_history_file(symbol, timeframe)
    file_deleted = False
    if os.path.exists(filename):
        try:
            os.remove(filename)
            file_deleted = True
        except Exception as e:
            return {"success": False, "error": f"Could not delete file: {e}"}
    meta_deleted = HistoryManager.remove_meta(symbol, timeframe)
    if file_deleted or meta_deleted:
        return {"success": True, "file_deleted": file_deleted, "meta_deleted": meta_deleted}
    else:
        return {"success": False, "error": "File and meta not found or already deleted."}

@app.post("/history/download")
def download_history(symbol: str = Body(...), timeframe: str = Body(...), start_date: str = Body(...), end_date: str = Body(...)):
    """Download historical data, save to file, and update meta JSON. Incremental: solo descarga lo que falta y nunca borra datos existentes."""
    filename = HistoryManager.get_history_file(symbol, timeframe)
    meta = HistoryManager.get_meta(symbol, timeframe)
    import pandas as pd
    from datetime import datetime
    req_start = pd.to_datetime(start_date)
    req_end = pd.to_datetime(end_date)
    min_date = max_date = None
    if meta:
        min_date = pd.to_datetime(meta['min_date'])
        max_date = pd.to_datetime(meta['max_date'])
    dfs = []
    # Descargar tramo anterior si es necesario
    if not min_date or req_start < min_date:
        fetch_start = req_start
        fetch_end = min_date - pd.Timedelta(days=1) if min_date else req_end
        limit = int((fetch_end - fetch_start).total_seconds() // 60) + 1
        try:
            df_prev = fetch_ohlcv(symbol, timeframe, limit)
            df_prev = df_prev[(df_prev['ts'] >= fetch_start) & (df_prev['ts'] <= fetch_end)]
            if not df_prev.empty:
                dfs.append(df_prev)
        except Exception as e:
            return {"success": False, "error": f"Error downloading previous data: {e}"}
    # Leer datos locales existentes
    if meta and os.path.exists(filename):
        try:
            df_local = pd.read_csv(filename, parse_dates=['ts'])
            if not df_local.empty:
                dfs.append(df_local)
        except Exception as e:
            return {"success": False, "error": f"Error reading local file: {e}"}
    # Descargar tramo posterior si es necesario
    if not max_date or req_end > max_date:
        fetch_start = (max_date + pd.Timedelta(days=1)) if max_date else req_start
        fetch_end = req_end
        limit = int((fetch_end - fetch_start).total_seconds() // 60) + 1
        try:
            df_next = fetch_ohlcv(symbol, timeframe, limit)
            df_next = df_next[(df_next['ts'] >= fetch_start) & (df_next['ts'] <= fetch_end)]
            if not df_next.empty:
                dfs.append(df_next)
        except Exception as e:
            return {"success": False, "error": f"Error downloading next data: {e}"}
    # Unir y limpiar duplicados (NO recortar al rango solicitado)
    if dfs:
        df_all = pd.concat(dfs, ignore_index=True)
        df_all = df_all.drop_duplicates(subset=['ts']).sort_values('ts')
        if df_all.empty:
            return {"success": False, "error": "No data available for the requested range."}
        df_all.to_csv(filename, index=False)
        # Actualizar meta al rango total disponible
        min_hist = df_all['ts'].min().isoformat()
        max_hist = df_all['ts'].max().isoformat()
        HistoryManager.update_meta(symbol, timeframe, min_hist, max_hist, os.path.basename(filename))
        return {"success": True, "history_file": filename, "min_date": min_hist, "max_date": max_hist}
    else:
        # Si existe el archivo pero no hay datos, lo eliminamos
        if os.path.exists(filename):
            os.remove(filename)
        HistoryManager.remove_meta(symbol, timeframe)
        return {"success": False, "error": "No data downloaded or available for the requested range."}

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
    hist_file = get_history_filename(req.symbol, timeframe)
    meta_file = get_history_meta_filename(req.symbol, timeframe)
    # Remove old/duplicate history files
    import glob
    s = req.symbol.replace('/', '-')
    pattern = os.path.join(HISTORY_DIR, f"history_{s}_{timeframe}_*.csv")
    for f in glob.glob(pattern):
        try:
            os.remove(f)
        except Exception:
            pass
    # Calculate the number of candles (limit) based on timeframe and date range
    try:
        tf_minutes = int(timeframe.replace('m','')) if 'm' in timeframe else 1
        dt_start = datetime.strptime(start_date[:10], "%Y-%m-%d")
        dt_end = datetime.strptime(end_date[:10], "%Y-%m-%d")
        n_minutes = int((dt_end - dt_start).total_seconds() // 60)
        limit = max(1000, n_minutes // tf_minutes + 10)
    except Exception:
        limit = 1000
    try:
        download_ohlcv_to_csv(symbol, timeframe, limit, hist_file)
        if os.path.exists(hist_file):
            df = pd.read_csv(hist_file)
            if 'ts' in df.columns:
                df['ts'] = pd.to_datetime(df['ts'])
                min_hist = df['ts'].min().strftime('%Y-%m-%d')
                max_hist = df['ts'].max().strftime('%Y-%m-%d')
                req_start = start_date[:10]
                req_end = end_date[:10]
                # Update meta.json
                meta = {"start_date": min_hist, "end_date": max_hist}
                with open(meta_file, 'w', encoding='utf-8') as f:
                    json.dump(meta, f)
                if req_start < min_hist or req_end > max_hist:
                    return {"success": False, "error": f"Downloaded history does not cover requested range: {req_start} to {req_end}. File covers {min_hist} to {max_hist}."}
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
    start_date: str = Query(None, description="Start date (YYYY-MM-DD HH:MM:SS)"),
    end_date: str = Query(None, description="End date (YYYY-MM-DD HH:MM:SS)")
):
    """
    Generic summary endpoint for any strategy. Allows filtering by date range.
    """
    # Build backtest file path
    file = os.path.join("data", "strategies", strategy, f"backtest_{symbol}_{timeframe}.csv")
    if not os.path.exists(file):
        raise HTTPException(status_code=404, detail=f"Backtest file not found: {file}")
    df = pd.read_csv(file)
    if 'ts' in df.columns:
        df['ts'] = pd.to_datetime(df['ts'])
    # Filtering by dates if specified
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

@app.get("/history_range/")
def history_range(strategy: str, symbol: str, timeframe: str):
    """
    Returns the available date range in the local historical file for the given strategy, symbol, and timeframe.
    """
    meta_file = get_history_meta_filename(symbol, timeframe)
    if not os.path.exists(meta_file):
        return {"success": False, "error": "No local history meta file found."}
    try:
        with open(meta_file, 'r', encoding='utf-8') as f:
            meta = json.load(f)
        return {"success": True, "start_date": meta.get('start_date'), "end_date": meta.get('end_date')}
    except Exception as e:
        return {"success": False, "error": f"Error reading meta file: {e}"}
