"""
Summary script for cross_ema backtest results.

This script loads the backtest CSV, simulates trades, and prints a performance summary.

Usage:
    python summary_cross_ema.py
"""

# Script de resumen de backtest para cross_ema
import pandas as pd

file = r"data/backtest_BTC-USDT_1m.csv"
df = pd.read_csv(file)

trades = []
position = None
entry_price = 0
for i, row in df.iterrows():
    signal = str(row['signal']).strip()
    price = row['close']
    if signal == 'BUY' and position is None:
        position = 'LONG'
        entry_price = price
        entry_time = row['ts']
    elif signal == 'SELL' and position == 'LONG':
        exit_price = price
        exit_time = row['ts']
        profit = exit_price - entry_price
        trades.append({
            'entry_time': entry_time,
            'entry_price': entry_price,
            'exit_time': exit_time,
            'exit_price': exit_price,
            'profit': profit
        })
        position = None

df_last = df.iloc[-1]
if position == 'LONG':
    trades.append({
        'entry_time': entry_time,
        'entry_price': entry_price,
        'exit_time': df_last['ts'],
        'exit_price': df_last['close'],
        'profit': df_last['close'] - entry_price
    })

trades_df = pd.DataFrame(trades)
n_trades = len(trades_df)
total_profit = trades_df['profit'].sum() if n_trades > 0 else 0
win_trades = trades_df[trades_df['profit'] > 0]
loss_trades = trades_df[trades_df['profit'] <= 0]
win_rate = len(win_trades) / n_trades * 100 if n_trades > 0 else 0
avg_profit = trades_df['profit'].mean() if n_trades > 0 else 0
if n_trades > 0:
    equity = trades_df['profit'].cumsum()
    peak = equity.cummax()
    drawdown = equity - peak
    max_drawdown = drawdown.min()
else:
    max_drawdown = 0

print("Resumen de Backtest cross_ema BTC-USDT 1m:")
print(f"Total de operaciones: {n_trades}")
print(f"Ganancia/Pérdida total: {total_profit:.2f}")
print(f"Operaciones ganadoras: {len(win_trades)}")
print(f"Operaciones perdedoras: {len(loss_trades)}")
print(f"Porcentaje de acierto: {win_rate:.2f}%")
print(f"Ganancia/Pérdida promedio por operación: {avg_profit:.2f}")
print(f"Drawdown máximo: {max_drawdown:.2f}")
if n_trades > 0:
    print("\nDetalle de operaciones:")
    print(trades_df)
