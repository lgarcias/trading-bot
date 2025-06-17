import React from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid, ResponsiveContainer, Legend } from 'recharts';

export default function BacktestResultPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const { summary, rawStdout, strategy, historyFile } = location.state || {};

  if (!summary && !rawStdout) {
    return (
      <div style={{ padding: 32 }}>
        <h2>No backtest result to display</h2>
        <button onClick={() => navigate('/backtest')}>Back to Backtest</button>
      </div>
    );
  }

  return (
    <div className="app-container">
      <h1>Backtest Summary</h1>
      <div style={{ marginBottom: 16 }}>
        <b>Strategy:</b> {strategy}<br />
        <b>Historical file:</b> {historyFile}
      </div>
      {summary && summary.strategy_params && (
        <div style={{marginBottom: 24}}>
          <h3>Strategy Parameters</h3>
          <ul style={{display:'flex', flexWrap:'wrap', gap:24, listStyle:'none', padding:0}}>
            {Object.entries(summary.strategy_params).map(([k, v]) => (
              <li key={k}><b>{k}:</b> {v !== null && v !== undefined ? v.toString() : '-'}</li>
            ))}
          </ul>
        </div>
      )}
      {summary ? (
        <>
          <div style={{display:'flex', gap:32, flexWrap:'wrap', marginBottom:24}}>
            <div><b>Total trades:</b> {summary.total_trades}</div>
            <div><b>Total profit/loss:</b> {Number(summary.total_profit).toFixed(2)}</div>
            <div><b>Max drawdown:</b> {Number(summary.max_drawdown).toFixed(2)}</div>
            <div><b>Start date:</b> {summary.start_date}</div>
            <div><b>End date:</b> {summary.end_date}</div>
          </div>
          <div style={{display:'flex', gap:32, flexWrap:'wrap'}}>
            <div style={{flex:1, minWidth:320}}>
              <h3>Equity Curve</h3>
              <ResponsiveContainer width="100%" height={200}>
                <LineChart data={Array.isArray(summary.equity_curve) ? summary.equity_curve.map((v, i) => ({ trade: i+1, equity: v })) : []}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="trade" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Line type="monotone" dataKey="equity" stroke="#8884d8" dot={false} />
                </LineChart>
              </ResponsiveContainer>
            </div>
            <div style={{flex:1, minWidth:320}}>
              <h3>Drawdown Curve</h3>
              <ResponsiveContainer width="100%" height={200}>
                <LineChart data={Array.isArray(summary.drawdown_curve) ? summary.drawdown_curve.map((v, i) => ({ trade: i+1, drawdown: v })) : []}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="trade" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Line type="monotone" dataKey="drawdown" stroke="#ff4d4f" dot={false} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>
          <h3 style={{marginTop:32}}>First 20 Trades</h3>
          <div style={{overflowX: 'auto', maxHeight: 200}}>
            <table style={{width: '100%', fontSize: '0.95em', borderCollapse: 'collapse'}}>
              <thead>
                <tr>
                  <th>Entry Time</th>
                  <th>Entry Price</th>
                  <th>Exit Time</th>
                  <th>Exit Price</th>
                  <th>Profit</th>
                </tr>
              </thead>
              <tbody>
                {Array.isArray(summary.trades) && summary.trades.map((t, i) => (
                  <tr key={i}>
                    <td>{t.entry_time || t.ts || ''}</td>
                    <td>{t.entry_price || t.close || ''}</td>
                    <td>{t.exit_time || ''}</td>
                    <td>{t.exit_price || ''}</td>
                    <td style={{color: t.profit >= 0 ? 'green' : 'red'}}>{t.profit !== undefined ? Number(t.profit).toFixed(2) : ''}</td>
                  </tr>
                ))}
              </tbody>
            </table>
            {Array.isArray(summary.trades) && summary.trades.length > 20 && <div style={{color: '#888', fontSize: '0.9em'}}>Showing first 20 trades...</div>}
          </div>
        </>
      ) : (
        <div style={{ background: '#f9f9f9', padding: 16, borderRadius: 8 }}>
          <pre style={{ whiteSpace: 'pre-wrap', wordBreak: 'break-word' }}>{rawStdout}</pre>
        </div>
      )}
      <button style={{ marginTop: 24 }} onClick={() => navigate('/backtest')}>Back to Backtest</button>
    </div>
  );
}
