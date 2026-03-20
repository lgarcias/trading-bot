# Algorithmic Trading Platform

## Overview
This project is an algorithmic trading platform designed to build, test, and evaluate trading strategies using historical market data.

It provides a modular system for defining trading strategies, a backtesting engine to simulate performance, and a web interface to manage and analyze results.

This project demonstrates a production-oriented architecture for data-driven decision systems.

---

## Why this project
I built this project to explore how trading systems are designed and how strategies can be evaluated before being used in real environments.

It also reflects my interest in building systems that combine data processing, decision logic, and user interaction — a key aspect of my work as a Technical Project Manager.

---

## Features
- Modular strategy system (plug-and-play strategies)
- Backtesting engine for historical data analysis
- Data collection and management
- REST API built with FastAPI
- Web interface (React) for interaction and visualization
- Automated testing with pytest
- Containerized setup with Docker

---

## What you can do
- Define and test trading strategies (e.g., moving average crossover)
- Run backtests on historical market data
- Compare strategy performance
- Analyze results to improve decision logic

---

## How it works
1. Market data is collected and stored  
2. A trading strategy defines buy/sell conditions  
3. The backtesting engine simulates trades  
4. Results are analyzed through the API or frontend  

---

## Tech Stack
- Python
- FastAPI
- React
- Pandas / NumPy
- Pytest
- Docker & Docker Compose

---

## Quick start

Start all services:

    docker compose up -d

Access the application:

- Backend API: http://localhost:8000  
- Frontend: http://localhost:3000  

👉 For a detailed guide, see: `docs/getting-started.md`

---

## Example

Strategy: Moving Average Crossover  
The system evaluates buy/sell signals based on short vs long moving averages and simulates performance over historical data.

---

## Documentation

- Getting started: `docs/getting-started.md`
- Architecture overview: `docs/architecture.md`
- Additional technical and development notes: `docs/`

---

## Future improvements
- Live trading integration (e.g., Binance API)
- Strategy optimization and parameter tuning
- Performance visualization dashboards
- Risk management features

---
