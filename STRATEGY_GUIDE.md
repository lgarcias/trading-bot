# How to Create and Configure a New Strategy

This guide explains the steps to add a new trading strategy to the crypto-bot project.

## 1. Create the Strategy Folder
- Go to `src/strategies/`.
- Create a new folder named after your strategy (e.g., `my_strategy`).

## 2. Add a Configuration File
- In your strategy folder, create a `config.yaml` file.
- Define parameters, allowed symbols, and any other settings needed by your strategy.

## 3. Implement the Signal Logic
- In `src/strategies/`, create a file like `my_strategy_func.py`.
- Implement a function that receives a DataFrame and returns 'BUY', 'SELL', or 'HOLD'.

## 4. Add Backtest and Summary Scripts
- In your strategy folder, add scripts such as:
  - `backtest_my_strategy.py` (for backtesting logic)
  - `my_strategy.py` (main logic, if needed)
  - `summary_my_strategy.py` (for result summaries)
- Use existing strategies as templates.

## 5. Register the Strategy in the Backend
- If required, add your strategy to any registry or list in the backend so it appears in the API and frontend.

## 6. (Optional) Add Tests
- Add tests in `tests/` to validate your strategy logic.

## 7. (Optional) Update the Frontend
- If the frontend allows strategy selection, add your new strategy to the list.

---

[← Back to README](README.md)
