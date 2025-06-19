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

## Strategy Development Guide

- [How to Create and Configure a New Strategy](STRATEGY_GUIDE.md)

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

## 📄 Roadmap Paper Trading

Consulta el plan y diseño del sistema de paper trading en el [Paper Trading Bot: Roadmap & Design](docs/Paper-Trading-Bot-Roadmap.md).

## 🚀 Migración a Docker

Consulta la guía para contenerizar y desplegar el proyecto en [Migracion-a-Docker.md](docs/Migracion-a-Docker.md).

## 🐳 Entorno Docker y Dev Container (recomendado)

Este proyecto está preparado para funcionar de forma óptima en un entorno Dockerizado usando Dev Containers de VS Code.

- **No necesitas instalar dependencias manualmente**: Al abrir el proyecto en VS Code y seleccionar "Reopen in Container", todo se instala automáticamente.
- **Sin conflictos de versiones ni problemas de permisos**: El contenedor ya incluye Python, Node, dependencias y extensiones necesarias.
- **Acceso a la app:**
  - Frontend: [http://localhost:5173](http://localhost:5173)
  - Backend (Swagger UI): [http://localhost:8000/docs](http://localhost:8000/docs)
- **¿No usas el contenedor?** Puedes seguir las instrucciones manuales más abajo.

Para detalles completos y solución de problemas, consulta la guía:
[docs/Entorno-Docker-y-DevContainer.md](docs/Entorno-Docker-y-DevContainer.md)

## Devcontainer: workspaceFolder automático

El archivo `.devcontainer/devcontainer.json` está configurado para que el directorio de trabajo sea `/app` y el volumen se monte ahí. Si tras un rebuild el valor de `workspaceFolder` cambia, se corrige automáticamente gracias al script `.devcontainer/fix_workspacefolder.py`, que se ejecuta tras cada rebuild mediante el campo `postCreateCommand`.

No necesitas hacer nada manualmente: si el valor vuelve a `/workspace`, el script lo corregirá a `/app`.
