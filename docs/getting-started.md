# Getting Started

## What is this project?

This is an algorithmic trading platform that allows you to design, test, and evaluate trading strategies using historical market data.

It is built as a modular system with a backend API, a strategy engine, and a frontend interface for interaction and analysis.

---

## Requirements

- Docker & Docker Compose installed
- (Optional) Node.js if running frontend manually
- (Optional) Python if running backend manually

---

## Quick start

Start all services using Docker:

    docker compose up -d

---

## Access the application

- Backend API: http://localhost:8000  
- Frontend: http://localhost:3000  

---

## Basic workflow

1. Load or collect historical market data  
2. Select or implement a trading strategy  
3. Run a backtest using the strategy  
4. Analyze the results  
5. Iterate and improve the strategy  

---

## Example use case

A common strategy is the **moving average crossover**:

- Buy when short-term average crosses above long-term average  
- Sell when it crosses below  

The system simulates this strategy on historical data and provides performance results.

---

## Running without Docker (optional)

### Backend

    uvicorn backend.app.main:app --reload

### Frontend

    cd frontend
    npm install
    npm run dev

---

## Next steps

- Explore the API endpoints
- Create your own trading strategies
- Extend the system with new features (live trading, optimization, etc.)

---

## Documentation

- Architecture: `docs/architecture.md`
- Development setup: `docs/development/`
- Roadmap: `docs/roadmap/`

---
