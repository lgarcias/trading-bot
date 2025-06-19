# Crypto Bot Trading Framework

A modular Python framework (FastAPI backend + React frontend) for developing, testing, and running algorithmic trading strategies on historical OHLCV data.

## Features
- Modular strategy system: easily add new strategies in `src/strategies/`.
- Backtesting engine with CSV input/output.
- Robust historical data management (incremental, paginated, global meta, API & frontend integration).
- Organized results and data per strategy in `data/strategies/<strategy>/`.
- Modern React frontend (Vite) for history management and usability.
- Pytest-based unit testing for strategies, core modules, and API endpoints.

## Project Structure
```
crypto-bot/
├── src/                  # Main source code (FastAPI backend)
│   ├── api.py            # FastAPI app (all API endpoints)
│   ├── history_manager.py# Robust history/meta management
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
├── frontend/             # React + Vite frontend (SPA)
│   ├── src/              # React components & pages
│   ├── vite.config.js    # Vite config (proxy /api, SPA fallback)
│   └── ...
├── data/                 # Historical and backtest data (excluded from git)
│   └── strategies/
│       ├── cross_sma/
│       └── cross_ema/
├── tests/                # Pytest unit tests (incl. API)
├── requirements.txt      # Python dependencies
└── README.md             # Project documentation
```

## Usage
### 1. Install backend dependencies
```
pip install -r requirements.txt
```

### 2. Install frontend dependencies
```
cd frontend
npm install
```

### 3. Run backend (FastAPI + Uvicorn)
```
# From project root
uvicorn src.api:app --reload
```

### 4. Run frontend (React + Vite)
```
cd frontend
npm run dev
```
This will start the frontend at http://localhost:5173 and the backend at http://localhost:8000. The Vite proxy automatically redirects `/api` routes to the backend.

### 5. Manage historical data from the frontend
- Access the history management page from the top menu.
- You can list, download (incremental and paginated), delete, and view historical data and global meta.
- All actions are performed via `/api/history/...` endpoints.

### 6. Main API Endpoints
- `/api/history/list` — List all historical datasets and their ranges.
- `/api/history/meta` — Returns the global meta for historical data.
- `/api/history/download` — Incremental download of historical data.
- `/api/history/{symbol}/{timeframe}` (DELETE) — Delete a historical dataset.
- `/api/history/range/` — Query the available range for a dataset.
- `/backtest/` — Run a backtest.

### 7. Run tests
See `tests/README_TESTS.md` for details. Example:
```
$env:PYTHONPATH="."; pytest --maxfail=2 --disable-warnings -v
```
API tests are in `tests/test_api.py` and cover the main endpoints.

## Strategy Development Guide

- [How to Create and Configure a New Strategy](STRATEGY_GUIDE.md)

## Data & Results
- All generated data and backtest results are stored in `data/strategies/<strategy>/`.
- The `data/` directory is excluded from git by default.

## License
MIT

---

## Production Deployment Note (Single Page Application Routing)

If you deploy the frontend in production (nginx, Apache, cloud static host), configure your server to serve `index.html` for all routes that **do not** start with `/api`. This ensures that refreshing or directly accessing any SPA route works correctly.

**Example nginx config:**
```nginx
location /api {
  proxy_pass http://localhost:8000;
}
location / {
  try_files $uri /index.html;
}
```

**For other servers or cloud hosts**, look for the "SPA fallback" or "history API fallback" option and enable it for your frontend build.

API routes (only `/api/...`) should be proxied or routed to the backend.

---

## 📄 Paper Trading Roadmap

See the plan and design for the paper trading system in [Paper Trading Bot: Roadmap & Design](docs/Paper-Trading-Bot-Roadmap.md).

## 🚀 Docker Migration Guide

See the guide for containerizing and deploying the project in [Migracion-a-Docker.md](docs/Migracion-a-Docker.md).

## 🐳 Docker & Dev Container Environment (Recommended)

This project is optimized to run in a Dockerized environment using VS Code Dev Containers.

- **No need to install dependencies manually**: When you open the project in VS Code and select "Reopen in Container", everything is installed automatically.
- **No version conflicts or permission issues**: The container already includes Python, Node, dependencies, and required extensions.
- **App access:**
  - Frontend: [http://localhost:5173](http://localhost:5173)
  - Backend (Swagger UI): [http://localhost:8000/docs](http://localhost:8000/docs)
- **Not using the container?** You can follow the manual instructions below.

For full details and troubleshooting, see the guide:
[docs/Entorno-Docker-y-DevContainer.md](docs/Entorno-Docker-y-DevContainer.md)

## Devcontainer: Automatic workspaceFolder

The `.devcontainer/devcontainer.json` file is configured so that the working directory is `/app` and the volume is mounted there. If after a rebuild the value of `workspaceFolder` changes, it is automatically fixed by the script `.devcontainer/fix_workspacefolder.py`, which runs after each rebuild via the `postCreateCommand` field.

---

## 🗄️ PostgreSQL Integration Roadmap
See [`docs/Postgres-Integration-Roadmap.md`](docs/Postgres-Integration-Roadmap.md) for a step-by-step plan to add PostgreSQL support to the app. This document explains how to migrate from file-based storage to a robust database backend, what changes are needed, and what future improvements are possible.
