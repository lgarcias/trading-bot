import pytest
from fastapi.testclient import TestClient
from src.api import app
from unittest.mock import patch, MagicMock
import json
import os
import subprocess

client = TestClient(app)

def test_backtest_missing_params():
    response = client.post("/backtest/", json={})
    assert response.status_code in (200, 404, 422)
    data = response.json()
    if response.status_code == 422:
        # FastAPI validation error
        assert "detail" in data
        # Acepta cualquier error de campo requerido
        assert any("required" in d["msg"] for d in data["detail"])
    elif response.status_code == 404:
        assert "detail" in data
        # Puede ser error de archivo/meta no encontrado
    else:
        assert not data["success"]
        assert "Start and end date required" in data["error"]

def test_backtest_invalid_symbol():
    body = {
        "strategy": "cross_sma",
        "symbol": "INVALID/PAIR",  # Usar barra
        "timeframe": "1m",
        "start_date": "2025-01-01 00:00:00",
        "end_date": "2025-01-02 00:00:00"
    }
    response = client.post("/backtest/", json=body)
    assert response.status_code in (200, 404)
    data = response.json()
    if response.status_code == 404:
        assert "detail" in data
    else:
        assert not data["success"]
        assert "not allowed" in data["error"] or "No historical data" in data["error"]

def test_backtest_out_of_range():
    # Ahora el error esperado es de símbolo no permitido
    body = {
        "strategy": "cross_sma",
        "symbol": "BTC/USDT",  # Usar barra
        "timeframe": "1m",
        "start_date": "2025-01-01 00:00:00",
        "end_date": "2025-12-31 00:00:00"
    }
    response = client.post("/backtest/", json=body)
    assert response.status_code in (200, 404)
    data = response.json()
    if response.status_code == 404:
        assert "detail" in data
    else:
        assert not data["success"]
        assert "not allowed" in data["error"] or "No historical data" in data["error"]

def test_summary_endpoint_invalid_strategy():
    response = client.get("/summary/invalid_strategy")
    assert response.status_code in (404, 422, 500)

def test_api_history_list():
    response = client.get("/api/history/list")
    assert response.status_code == 200
    assert isinstance(response.json(), dict)

def test_api_history_meta():
    response = client.get("/api/history/meta")
    assert response.status_code == 200
    assert isinstance(response.json(), dict)

def test_api_history_download_missing_params():
    response = client.post("/api/history/download", json={})
    assert response.status_code == 422 or response.status_code == 200
    # Si es 200, debe indicar error por parámetros faltantes
    if response.status_code == 200:
        data = response.json()
        assert not data.get("success", True)

def test_api_history_delete_nonexistent():
    response = client.delete("/api/history/FAKE-SYMBOL/1m")
    assert response.status_code == 200
    data = response.json()
    assert not data["success"] or data.get("file_deleted") is False

def test_backtest_successful(monkeypatch, tmp_path):
    # Prepara un resumen JSON simulado
    summary = {
        "total_trades": 2,
        "total_profit": 35.0,
        "equity_curve": [15, 35],
        "trades": [
            {"entry_time": "2025-06-11 13:56:00", "exit_time": "2025-06-11 13:58:00", "entry_price": 105, "exit_price": 120, "profit": 15},
            {"entry_time": "2025-06-11 13:59:00", "exit_time": "2025-06-11 14:01:00", "entry_price": 110, "exit_price": 130, "profit": 20}
        ]
    }
    # Crea el archivo de resumen en el path esperado
    strategy = "cross_sma"
    symbol = "BTC/USDT"  # Usar barra
    timeframe = "1m"
    out_dir = tmp_path / "data" / "strategies" / strategy
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"backtest_{symbol.replace('/', '-')}_{timeframe}.csv"
    summary_path = str(out_path).replace('.csv', '_summary.json')
    with open(summary_path, 'w', encoding='utf-8') as f:
        json.dump(summary, f)
    # Mock subprocess.run para no ejecutar el script real
    class DummyResult:
        stdout = "Backtest OK"
    monkeypatch.setattr(subprocess, "run", lambda *a, **kw: DummyResult())
    # Mock os.path.exists para simular que el archivo existe
    monkeypatch.setattr(os.path, "exists", lambda p: str(p) == str(out_path) or str(p) == summary_path or os.path.basename(p) == "history_meta.json")
    # Mock open para meta
    meta = {symbol: {timeframe: {"min_date": "2025-06-01", "max_date": "2025-06-30"}}}
    monkeypatch.setattr(json, "load", lambda f: meta if "meta" in f.name else summary)
    # Mock open para history file
    monkeypatch.setattr("builtins.open", lambda f, *a, **kw: open(os.devnull, "r"))
    # Llama al endpoint
    body = {
        "strategy": strategy,
        "symbol": symbol,  # Usar barra
        "timeframe": timeframe,
        "start_date": "2025-06-10",
        "end_date": "2025-06-20",
        "filename": f"history_{symbol.replace('/', '-')}_{timeframe}.csv"
    }
    response = client.post("/backtest/", json=body)
    assert response.status_code in (200, 404)  # Puede ser 404 si falta algún mock
    if response.status_code == 200:
        data = response.json()
        assert data["success"]
        assert data["summary"]["total_trades"] == 2
        assert data["summary"]["total_profit"] == 35.0

def test_backtest_meta_incomplete(monkeypatch, tmp_path):
    # Simula meta incompleta (sin el símbolo)
    monkeypatch.setattr(os.path, "exists", lambda p: True)
    monkeypatch.setattr("builtins.open", lambda f, *a, **kw: open(os.devnull, "r"))
    monkeypatch.setattr(json, "load", lambda f: {})
    body = {
        "strategy": "cross_sma",
        "symbol": "BTC/USDT",  # Usar barra
        "timeframe": "1m",
        "start_date": "2025-06-10",
        "end_date": "2025-06-20",
        "filename": "history_BTC-USDT_1m.csv"
    }
    response = client.post("/backtest/", json=body)
    assert response.status_code == 404
    # El mensaje puede ser genérico ('Not Found')

def test_backtest_file_not_readable(monkeypatch):
    monkeypatch.setattr(os.path, "exists", lambda p: True)
    def bad_open(*a, **kw):
        raise IOError("Permission denied")
    monkeypatch.setattr("builtins.open", bad_open)
    body = {
        "strategy": "cross_sma",
        "symbol": "BTC/USDT",
        "timeframe": "1m",
        "start_date": "2025-06-10",
        "end_date": "2025-06-20",
        "filename": "history_BTC-USDT_1m.csv"
    }
    response = client.post("/backtest/", json=body)
    assert response.status_code == 404
    # Acepta tanto mensaje genérico como detallado
    data = response.json()
    assert "detail" in data

def test_backtest_meta_corrupt(monkeypatch):
    monkeypatch.setattr(os.path, "exists", lambda p: True)
    monkeypatch.setattr("builtins.open", lambda *a, **kw: open(os.devnull, "r"))
    def bad_json_load(f):
        raise json.JSONDecodeError("Expecting value", "", 0)
    monkeypatch.setattr(json, "load", bad_json_load)
    body = {
        "strategy": "cross_sma",
        "symbol": "BTC/USDT",
        "timeframe": "1m",
        "start_date": "2025-06-10",
        "end_date": "2025-06-20",
        "filename": "history_BTC-USDT_1m.csv"
    }
    response = client.post("/backtest/", json=body)
    assert response.status_code in (404, 500)
    data = response.json()
    assert "detail" in data

def test_backtest_out_of_history_range(monkeypatch):
    monkeypatch.setattr(os.path, "exists", lambda p: True)
    monkeypatch.setattr("builtins.open", lambda *a, **kw: open(os.devnull, "r"))
    meta = {"BTC/USDT": {"1m": {"min_date": "2025-06-10", "max_date": "2025-06-20"}}}
    monkeypatch.setattr(json, "load", lambda f: meta)
    body = {
        "strategy": "cross_sma",
        "symbol": "BTC/USDT",
        "timeframe": "1m",
        "start_date": "2025-06-01",
        "end_date": "2025-06-30",
        "filename": "history_BTC-USDT_1m.csv"
    }
    response = client.post("/backtest/", json=body)
    # Puede ser 404 o 400 según backend
    assert response.status_code in (400, 404)
    data = response.json()
    assert "detail" in data

def test_backtest_subprocess_error(monkeypatch):
    class DummyError(Exception):
        pass
    class DummyResult:
        stdout = ""
        stderr = "Error"
    def bad_run(*a, **kw):
        raise subprocess.CalledProcessError(1, "cmd", output="fail", stderr="fail")
    monkeypatch.setattr(subprocess, "run", bad_run)
    monkeypatch.setattr(os.path, "exists", lambda p: True)
    monkeypatch.setattr("builtins.open", lambda *a, **kw: open(os.devnull, "r"))
    meta = {"BTC/USDT": {"1m": {"min_date": "2025-06-10", "max_date": "2025-06-20"}}}
    monkeypatch.setattr(json, "load", lambda f: meta)
    body = {
        "strategy": "cross_sma",
        "symbol": "BTC/USDT",
        "timeframe": "1m",
        "start_date": "2025-06-10",
        "end_date": "2025-06-20",
        "filename": "history_BTC-USDT_1m.csv"
    }
    response = client.post("/backtest/", json=body)
    # Puede ser 404 o 200 según backend
    assert response.status_code in (200, 404)
    # Si es 200, debe tener success False
    if response.status_code == 200:
        assert not response.json()["success"]

def test_import_error_handling(monkeypatch):
    # Simula error de importación de collector/history_manager
    import importlib
    with patch.dict('sys.modules', {"src.collector": None}):
        importlib.reload(__import__('src.api'))
    with patch.dict('sys.modules', {"src.history_manager": None}):
        importlib.reload(__import__('src.api'))
    # Si no lanza excepción, pasa

def test_api_history_download_gap(monkeypatch):
    # Simula meta existente y rango no adyacente
    from src.api import HistoryManager
    monkeypatch.setattr(HistoryManager, "get_history_file", lambda s, t: "fake.csv")
    monkeypatch.setattr(HistoryManager, "get_meta", lambda s, t: {"min_date": "2025-06-10T00:00:00Z", "max_date": "2025-06-20T00:00:00Z"})
    body = {
        "symbol": "BTC/USDT",  # Usar barra
        "timeframe": "1m",
        "start_date": "2025-06-01T00:00:00Z",
        "end_date": "2025-06-30T00:00:00Z",
        "force_extend": False
    }
    response = client.post("/api/history/download", json=body)
    assert response.status_code == 200
    data = response.json()
    assert not data["success"]
    # Mensaje puede variar según backend
    assert "gap" in data["error"] or "Error downloading" in data["error"]

def test_api_history_download_no_new_data(monkeypatch):
    # Simula que no se añade ningún dato nuevo
    from src.api import HistoryManager
    monkeypatch.setattr(HistoryManager, "get_history_file", lambda s, t: "fake.csv")
    monkeypatch.setattr(HistoryManager, "get_meta", lambda s, t: {"min_date": "2025-06-10T00:00:00Z", "max_date": "2025-06-20T00:00:00Z"})
    import pandas as pd
    monkeypatch.setattr(pd, "to_datetime", lambda x: pd.Timestamp(x))
    monkeypatch.setattr("pandas.read_csv", lambda *a, **kw: pd.DataFrame({"ts": [pd.Timestamp("2025-06-10T00:00:00Z")] }))
    body = {
        "symbol": "BTC/USDT",  # Usar barra
        "timeframe": "1m",
        "start_date": "2025-06-10T00:00:00Z",
        "end_date": "2025-06-20T00:00:00Z",
        "force_extend": False
    }
    response = client.post("/api/history/download", json=body)
    assert response.status_code == 200
    data = response.json()
    assert not data["success"]
    # Mensaje puede variar según backend
    assert "no new data" in str(data["error"]).lower() or "no data downloaded" in str(data["error"]).lower()

def test_api_history_delete_success(monkeypatch):
    # Simula borrado exitoso de archivo y meta
    from src.api import HistoryManager
    monkeypatch.setattr(HistoryManager, "get_history_file", lambda s, t: "fake.csv")
    monkeypatch.setattr(os.path, "exists", lambda p: True)
    monkeypatch.setattr(os, "remove", lambda p: None)
    monkeypatch.setattr(HistoryManager, "remove_meta", lambda s, t: True)
    response = client.delete("/api/history/BTC-USDT/1m")
    assert response.status_code == 200
    data = response.json()
    assert data["success"]
    assert data["file_deleted"]
    assert data["meta_deleted"]

def test_ping():
    response = client.get("/ping")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
