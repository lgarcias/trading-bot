import pytest
from fastapi.testclient import TestClient
from src.api import app

client = TestClient(app)

def test_backtest_missing_params():
    response = client.post("/backtest/", json={})
    assert response.status_code in (200, 422)
    data = response.json()
    if response.status_code == 422:
        # FastAPI validation error
        assert "detail" in data
        # Acepta cualquier error de campo requerido
        assert any("required" in d["msg"] for d in data["detail"])
    else:
        assert not data["success"]
        assert "Start and end date required" in data["error"]

def test_backtest_invalid_symbol():
    body = {
        "strategy": "cross_sma",
        "symbol": "INVALID/PAIR",
        "timeframe": "1m",
        "start_date": "2025-01-01 00:00:00",
        "end_date": "2025-01-02 00:00:00"
    }
    response = client.post("/backtest/", json=body)
    assert response.status_code == 200
    data = response.json()
    assert not data["success"]
    assert "not allowed" in data["error"] or "No historical data" in data["error"]

def test_backtest_out_of_range():
    # Ahora el error esperado es de símbolo no permitido
    body = {
        "strategy": "cross_sma",
        "symbol": "BTC-USDT",
        "timeframe": "1m",
        "start_date": "2025-01-01 00:00:00",
        "end_date": "2025-12-31 00:00:00"
    }
    response = client.post("/backtest/", json=body)
    assert response.status_code == 200
    data = response.json()
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
