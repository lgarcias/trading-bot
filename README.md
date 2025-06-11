# Crypto Bot Trading Framework

A modular Python framework for developing, testing, and running algorithmic trading strategies on historical OHLCV data.

## Features
- Modular strategy system: add new strategies easily in `src/strategies/`.
- Backtesting engine with CSV input/output.
- Historical data collection and management.
- Organized results and data per strategy in `data/strategies/<strategy>/`.
- Pytest-based unit testing for strategies and core modules.

## Project Structure
```
crypto-bot/
├── src/                  # Main source code
│   ├── backtest.py       # Backtesting engine
│   ├── collector.py      # Data collection utilities
│   ├── config.py         # Global configuration
│   ├── strategies.py     # Strategy loader/registry
│   ├── run.py            # Main bot runner
│   ├── move_strategy_data.py # Move backtest results to strategy folders
│   └── strategies/       # Strategy implementations
│       ├── cross_sma_func.py
│       ├── cross_ema_func.py
│       ├── cross_sma/    # cross_sma scripts
│       └── cross_ema/    # cross_ema scripts
├── data/                 # Historical and backtest data (excluded from git)
│   └── strategies/
│       ├── cross_sma/
│       └── cross_ema/
├── tests/                # Pytest unit tests
├── requirements.txt      # Python dependencies
└── README.md             # Project documentation
```

## Usage
### 1. Install dependencies
```
pip install -r requirements.txt
```

### 2. Download historical data
Edit `src/config.py` to set your symbol, timeframe, and strategy parameters. Then run:
```
python -m src.collector
```

### 3. Run a backtest
```
python -m src.backtest
```
Or use the per-strategy scripts in `src/strategies/<strategy>/`.

### 4. Move backtest results to strategy folders
```
python src/move_strategy_data.py <strategy> <symbol> <timeframe>
```
You can also specify a custom data directory (useful for testing or advanced usage):
```
python src/move_strategy_data.py <strategy> <symbol> <timeframe> --base-dir <your_data_dir>
```

### 5. Run tests
See `tests/README_TESTS.md` for details. Example:
```
$env:PYTHONPATH="."; pytest --maxfail=2 --disable-warnings -v
```

## Adding a New Strategy
1. Create a new function in `src/strategies/<your_strategy>_func.py`.
2. Optionally, add a subfolder in `src/strategies/` for scripts and analysis.
3. Register and test your strategy as shown in the examples.

## Data & Results
- All generated data and backtest results are stored in `data/strategies/<strategy>/`.
- The `data/` directory is excluded from git by default.

## License
MIT
