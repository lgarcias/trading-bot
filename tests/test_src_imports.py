import pytest
import importlib

def test_import_backtest():
    importlib.import_module('src.backtest')

def test_import_collector():
    importlib.import_module('src.collector')

def test_import_config():
    importlib.import_module('src.config')

def test_import_monkeypatch_numpy():
    importlib.import_module('src.monkeypatch_numpy')

def test_import_run():
    importlib.import_module('src.run')

def test_import_strategies():
    importlib.import_module('src.strategies')
