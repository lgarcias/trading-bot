"""
FastAPI backend to trigger backtesting for a selected strategy.
"""
from fastapi import FastAPI, Query, HTTPException, Body, Request, Path
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import subprocess
import os
import sys
from typing import Optional
from fastapi.middleware.cors import CORSMiddleware
import yaml
import json

app = FastAPI(title="Crypto Bot Backtest API")

# Enable CORS to allow requests from the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

HISTORY_DIR = os.path.join("data", "history")
os.makedirs(HISTORY_DIR, exist_ok=True)

def get_history_filename(symbol, timeframe):
    s = symbol.replace('/', '-')
    return os.path.join(HISTORY_DIR, f"history_{s}_{timeframe}.csv")

def get_history_meta_filename(symbol, timeframe):
    s = symbol.replace('/', '-')
    return os.path.join(HISTORY_DIR, f"history_{s}_{timeframe}.meta.json")

class BacktestRequest(BaseModel):
    strategy: str
    symbol: str
    timeframe: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    filename: Optional[str] = None  # New: allow frontend to specify the exact file
    # Optional: add more params as needed

class HistoryDownloadRequest(BaseModel):
    symbol: str = Field(..., example="BTC/USDT", description="Trading symbol, e.g. 'BTC/USDT'")
    timeframe: str = Field(..., example="1m", description="Timeframe, e.g. '1m', '5m', '1d'")
    start_date: str = Field(..., example="2024-01-01T00:00:00Z", description="Start date in ISO format")
    end_date: str = Field(..., example="2024-01-31T23:59:00Z", description="End date in ISO format")
    force_extend: bool = Field(False, example=False, description="Force extend range if not adjacent")

class HistoryMetaResponse(BaseModel):
    filename: str = Field(..., example="history_BTC-USDT_1m.csv")
    min_date: str = Field(..., example="2024-01-01T00:00:00Z")
    max_date: str = Field(..., example="2024-01-31T23:59:00Z")

def load_strategy_config(strategy: str):
    config_path = os.path.join("src", "strategies", strategy, "config.yaml")
    if not os.path.exists(config_path):
        return None
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

@app.post("/api/backtest/")
def run_backtest(req: BacktestRequest):
    """
    Run the backtest for the given strategy, symbol, timeframe, and date range.
    """
    # Normalizar símbolo a formato con barra para la API
    symbol = req.symbol.replace('-', '/')
    timeframe = req.timeframe
    start_date = getattr(req, 'start_date', None)
    end_date = getattr(req, 'end_date', None)
    filename = getattr(req, 'filename', None)
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
    # Use the filename if provided, else compute it
    if filename:
        hist_file = os.path.join(HISTORY_DIR, filename)
    else:
        hist_file = get_history_filename(symbol, timeframe)
    meta_path = os.path.join(HISTORY_DIR, 'history_meta.json')
    import logging
    abs_hist_file = os.path.abspath(hist_file)
    test_exists = os.path.exists(hist_file)
    test_read = False
    read_error = None
    try:
        with open(hist_file, 'r', encoding='utf-8') as f:
            f.readline()
            test_read = True
    except Exception as e:
        read_error = str(e)
        logging.warning(f"[BACKTEST] Error reading file: {e}")
    if not test_exists:
        detail = {
            "file": abs_hist_file,
            "exists": test_exists,
            "readable": test_read,
            "read_error": read_error
        }
        raise HTTPException(status_code=404, detail={"msg": "Historical data file not found or not readable", **detail})
    # Use global meta
    if not os.path.exists(meta_path):
        raise HTTPException(status_code=404, detail={"msg": "Global history_meta.json not found", "file": os.path.abspath(meta_path)})
    with open(meta_path, 'r', encoding='utf-8') as f:
        meta = json.load(f)
    # Find info for symbol/timeframe
    symbol_meta = meta.get(symbol)
    if not symbol_meta:
        raise HTTPException(status_code=404, detail={"msg": f"No meta info for symbol {symbol}", "symbol": symbol})
    tf_meta = symbol_meta.get(timeframe)
    if not tf_meta:
        raise HTTPException(status_code=404, detail={"msg": f"No meta info for timeframe {timeframe} in symbol {symbol}", "symbol": symbol, "timeframe": timeframe})
    min_hist = tf_meta.get('min_date')
    max_hist = tf_meta.get('max_date')
    req_start = start_date[:10]
    req_end = end_date[:10]
    if req_start < min_hist[:10] or req_end > max_hist[:10]:
        raise HTTPException(status_code=400, detail={"msg": f"Requested range {req_start} to {req_end} is outside local history range ({min_hist} to {max_hist})"})
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
            # Buscar y devolver el resumen JSON si existe
            summary_path = out_path.replace('.csv', '_summary.json')
            summary = None
            if os.path.exists(summary_path):
                try:
                    with open(summary_path, 'r', encoding='utf-8') as f:
                        summary = json.load(f)
                except Exception as e:
                    summary = None
            return {
                "success": True,
                "result_file": out_path,
                "stdout": result.stdout,
                "summary": summary
            }
        # Search by pattern if there are naming issues
        pattern = os.path.join("data", "strategies", req.strategy, f"backtest_{symbol.replace('/', '-')}*{timeframe}.csv")
        matches = glob.glob(pattern)
        if matches:
            # Buscar y devolver el resumen JSON si existe para el primer match
            summary_path = matches[0].replace('.csv', '_summary.json')
            summary = None
            if os.path.exists(summary_path):
                try:
                    with open(summary_path, 'r', encoding='utf-8') as f:
                        summary = json.load(f)
                except Exception as e:
                    summary = None
            return {
                "success": True,
                "result_file": matches[0],
                "stdout": result.stdout,
                "summary": summary
            }
        return {"success": False, "error": "Backtest completed but result file not found.", "stdout": result.stdout}
    except subprocess.CalledProcessError as e:
        return {"success": False, "error": str(e), "stdout": e.stdout, "stderr": e.stderr}

@app.get("/api/history/list", summary="List available historical files", 
         description="Returns all available historical files and their date ranges.",
         response_description="A dictionary with all available symbols and their timeframes.")
def list_history():
    """List all available historical files and their date ranges."""
    return HistoryManager.list_all()

@app.get("/api/history/meta", summary="Get global history meta info", 
         description="Returns the global meta JSON for all historical files, including min/max dates.",
         response_description="A dictionary with meta info for all symbols and timeframes.")
def get_history_meta():
    """Return the full meta JSON for all historical files."""
    return HistoryManager.list_all()

@app.delete(
    "/api/history/{symbol:path}/{timeframe}",
    summary="Delete a historical file",
    description="Deletes a historical file and updates the meta JSON. Returns success status.",
    response_description="Success status and details about file/meta deletion."
)
def delete_history(
    symbol: str = Path(..., example="BTC/USDT", description="Trading symbol, e.g. 'BTC/USDT'"),
    timeframe: str = Path(..., example="1m", description="Timeframe, e.g. '1m', '5m', '1d'")
):
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

@app.post(
    "/api/history/download",
    summary="Download historical data",
    description="Downloads historical data for a symbol/timeframe and updates the meta JSON. Prevents gaps unless 'force_extend' is set.",
    response_description="Success status, file info, and range details.",
    response_model=None,
    responses={
        200: {
            "description": "Download result",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "updated": True,
                        "history_file": "data/history/history_BTC-USDT_1m.csv",
                        "min_date": "2024-01-01T00:00:00Z",
                        "max_date": "2024-01-31T23:59:00Z",
                        "anterior_total_pages": 1,
                        "anterior_completed_pages": 1,
                        "posterior_total_pages": 0,
                        "posterior_completed_pages": 0
                    }
                }
            }
        }
    }
)
def download_history(
    symbol: str = Body(..., example="BTC/USDT"),
    timeframe: str = Body(..., example="1m"),
    start_date: str = Body(..., example="2024-01-01T00:00:00Z"),
    end_date: str = Body(..., example="2024-01-31T23:59:00Z"),
    force_extend: bool = Body(False, example=False)
):
    # Normalizar símbolo a formato con barra para la API
    symbol = symbol.replace('-', '/')
    """Download historical data, save to file, and update meta JSON. No permite crear gaps: si el rango solicitado no es adyacente, sugiere el rango correcto y requiere confirmación."""
    filename = HistoryManager.get_history_file(symbol, timeframe)
    meta = HistoryManager.get_meta(symbol, timeframe)
    import pandas as pd
    from datetime import datetime, timedelta
    req_start = pd.to_datetime(start_date)
    req_end = pd.to_datetime(end_date)
    min_date = max_date = None
    max_limit = 1000
    dfs = []
    new_data_added = False
    anterior_total_pages = anterior_completed_pages = 0
    posterior_total_pages = posterior_completed_pages = 0
    if meta:
        min_date = pd.to_datetime(meta['min_date'])
        max_date = pd.to_datetime(meta['max_date'])
        # Comprobar si el rango solicitado es adyacente
        adyacente = (
            req_start <= min_date - pd.Timedelta(minutes=5) or
            req_end >= max_date + pd.Timedelta(minutes=5) or
            (req_start >= min_date and req_end <= max_date)
        )
        if not adyacente and not force_extend:
            # Sugerir el rango correcto
            new_min = min(req_start, min_date)
            new_max = max(req_end, max_date)
            return {
                "success": False,
                "error": "La descarga solicitada provocaría un gap en los datos. Solo se permiten descargas adyacentes al rango actual.",
                "current_min_date": min_date.isoformat(),
                "current_max_date": max_date.isoformat(),
                "suggested_start_date": new_min.isoformat(),
                "suggested_end_date": new_max.isoformat(),
                "force_extend_param": True
            }
        # Si force_extend, ampliar el rango
        if not adyacente and force_extend:
            req_start = min(req_start, min_date)
            req_end = max(req_end, max_date)
    # Descargar tramo anterior si es necesario
    if not min_date or req_start < min_date:
        fetch_start = req_start
        fetch_end = min_date - pd.Timedelta(minutes=5) if min_date else req_end
        all_prev = []
        current = fetch_start
        total_minutes = int((fetch_end - fetch_start).total_seconds() // 60)
        anterior_total_pages = (total_minutes // (5*max_limit)) + 1 if total_minutes > 0 else 0
        while current <= fetch_end:
            next_end = min(current + timedelta(minutes=5*max_limit-5), fetch_end)
            limit = int((next_end - current).total_seconds() // 60 // 5) + 1
            try:
                df_prev = fetch_ohlcv(symbol, timeframe, limit, since=current)
                if df_prev is not None and not df_prev.empty:
                    all_prev.append(df_prev)
                    current = df_prev['ts'].max() + pd.Timedelta(minutes=5)
                    anterior_completed_pages += 1
                    if current > fetch_end:
                        break
                else:
                    break
            except Exception as e:
                return {"success": False, "error": f"Error downloading previous data: {e}", "anterior_total_pages": anterior_total_pages, "anterior_completed_pages": anterior_completed_pages}
        if all_prev:
            df_prev_all = pd.concat(all_prev, ignore_index=True)
            df_prev_all = df_prev_all[(df_prev_all['ts'] >= fetch_start) & (df_prev_all['ts'] <= fetch_end)]
            if not df_prev_all.empty:
                dfs.append(df_prev_all)
                new_data_added = True
            else:
                return {"success": False, "error": f"No data downloaded for requested range {fetch_start} to {fetch_end} (anterior).", "anterior_total_pages": anterior_total_pages, "anterior_completed_pages": anterior_completed_pages}
        else:
            return {"success": False, "error": f"No data downloaded for requested range {fetch_start} to {fetch_end} (anterior).", "anterior_total_pages": anterior_total_pages, "anterior_completed_pages": anterior_completed_pages}
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
        fetch_start = (max_date + pd.Timedelta(minutes=5)) if max_date else req_start
        fetch_end = req_end
        all_next = []
        current = fetch_start
        total_minutes = int((fetch_end - fetch_start).total_seconds() // 60)
        posterior_total_pages = (total_minutes // (5*max_limit)) + 1 if total_minutes > 0 else 0
        while current <= fetch_end:
            next_end = min(current + timedelta(minutes=5*max_limit-5), fetch_end)
            limit = int((next_end - current).total_seconds() // 60 // 5) + 1
            try:
                df_next = fetch_ohlcv(symbol, timeframe, limit, since=current)
                if df_next is not None and not df_next.empty:
                    all_next.append(df_next)
                    current = df_next['ts'].max() + pd.Timedelta(minutes=5)
                    posterior_completed_pages += 1
                    if current > fetch_end:
                        break
                else:
                    break
            except Exception as e:
                return {"success": False, "error": f"Error downloading next data: {e}", "posterior_total_pages": posterior_total_pages, "posterior_completed_pages": posterior_completed_pages}
        if all_next:
            df_next_all = pd.concat(all_next, ignore_index=True)
            df_next_all = df_next_all[(df_next_all['ts'] >= fetch_start) & (df_next_all['ts'] <= fetch_end)]
            if not df_next_all.empty:
                dfs.append(df_next_all)
                new_data_added = True
            else:
                return {"success": False, "error": f"No data downloaded for requested range {fetch_start} to {fetch_end} (posterior).", "posterior_total_pages": posterior_total_pages, "posterior_completed_pages": posterior_completed_pages}
        else:
            return {"success": False, "error": f"No data downloaded for requested range {fetch_start} to {fetch_end} (posterior).", "posterior_total_pages": posterior_total_pages, "posterior_completed_pages": posterior_completed_pages}
    # Unir y limpiar duplicados (NO recortar al rango solicitado)
    if dfs:
        df_all = pd.concat(dfs, ignore_index=True)
        df_all = df_all.drop_duplicates(subset=['ts']).sort_values('ts')
        if df_all.empty:
            return {"success": False, "error": "No data available for the requested range."}
        # Solo guardar si hay datos nuevos
        if new_data_added:
            df_all.to_csv(filename, index=False)
            # Actualizar meta al rango total disponible
            min_hist = df_all['ts'].min().isoformat()
            max_hist = df_all['ts'].max().isoformat()
            HistoryManager.update_meta(symbol, timeframe, min_hist, max_hist, os.path.basename(filename))
            return {
                "success": True,
                "updated": True,
                "history_file": filename,
                "min_date": min_hist,
                "max_date": max_hist,
                "anterior_total_pages": anterior_total_pages,
                "anterior_completed_pages": anterior_completed_pages,
                "posterior_total_pages": posterior_total_pages,
                "posterior_completed_pages": posterior_completed_pages
            }
        else:
            return {
                "success": False,
                "updated": False,
                "error": "No new data was added. Local file already covers the requested range.",
                "anterior_total_pages": anterior_total_pages,
                "anterior_completed_pages": anterior_completed_pages,
                "posterior_total_pages": posterior_total_pages,
                "posterior_completed_pages": posterior_completed_pages
            }
    else:
        # Si existe el archivo pero no hay datos, lo eliminamos
        if os.path.exists(filename):
            os.remove(filename)
        HistoryManager.remove_meta(symbol, timeframe)
        return {"success": False, "error": "No data downloaded or available for the requested range."}

@app.get(
    "/ping",
    summary="Health check",
    description="Simple health check endpoint. Returns status 'ok' if the API is running.",
    response_description="Status message.",
    responses={
        200: {
            "description": "API is healthy",
            "content": {
                "application/json": {
                    "example": {"status": "ok"}
                }
            }
        }
    }
)
def ping():
    """Simple health check endpoint."""
    return {"status": "ok"}

import sys
try:
    from src.collector import download_ohlcv_to_csv, fetch_ohlcv
except Exception:
    print("Error importing collector:", file=sys.stderr)
try:
    from src.history_manager import HistoryManager
except Exception:
    print("Error importing history_manager:", file=sys.stderr)
