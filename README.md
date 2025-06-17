# Crypto Bot Trading Framework

A modular Python framework (FastAPI backend + React frontend) for developing, testing, and running algorithmic trading strategies on historical OHLCV data.

## Features
- Modular strategy system: add new strategies easily in `src/strategies/`.
- Backtesting engine with CSV input/output.
- Robust historical data management (incremental, paginated, meta global, API & frontend integration).
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
Esto levantará el frontend en http://localhost:5173 y el backend en http://localhost:8000. El proxy de Vite redirige automáticamente las rutas `/api` al backend.

### 5. Gestión de históricos desde el frontend
- Accede a la página de gestión de históricos desde el menú superior.
- Puedes listar, descargar (incremental y paginado), borrar y consultar históricos y meta global.
- Todo se realiza vía los endpoints `/api/history/...`.

### 6. Endpoints principales de la API
- `/api/history/list` — Lista todos los históricos y sus rangos.
- `/api/history/meta` — Devuelve el meta global de históricos.
- `/api/history/download` — Descarga incremental de históricos.
- `/api/history/{symbol}/{timeframe}` (DELETE) — Borra un histórico.
- `/api/history/range/` — Consulta el rango disponible para un histórico.
- `/backtest/` — Ejecuta un backtest.

### 7. Run tests
Ver `tests/README_TESTS.md` para detalles. Ejemplo:
```
$env:PYTHONPATH="."; pytest --maxfail=2 --disable-warnings -v
```
Los tests de API están en `tests/test_api.py` y cubren los endpoints principales.

## Adding a New Strategy
1. Crea una nueva función en `src/strategies/<your_strategy>_func.py`.
2. Opcionalmente, añade una subcarpeta en `src/strategies/` para scripts y análisis.
3. Registra y prueba tu estrategia como en los ejemplos.

## Data & Results
- Todos los datos generados y resultados de backtest se almacenan en `data/strategies/<strategy>/`.
- El directorio `data/` está excluido de git por defecto.

## License
MIT

---

## Production deployment note (Single Page Application routing)

Si despliegas el frontend en producción (nginx, Apache, cloud static host), configura tu servidor para servir `index.html` para todas las rutas que **no** empiecen por `/api`. Así, el refresco o acceso directo a cualquier ruta SPA funcionará correctamente.

**Ejemplo nginx config:**
```nginx
location /api {
  proxy_pass http://localhost:8000;
}
location / {
  try_files $uri /index.html;
}
```

**Para otros servidores o cloud hosts**, busca la opción "SPA fallback" o "history API fallback" y actívala para tu build frontend.

Las rutas de API (solo `/api/...`) deben ser proxyeadas o ruteadas al backend.

---
