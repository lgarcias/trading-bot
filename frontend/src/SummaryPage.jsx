import React, { useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid, ResponsiveContainer, Legend } from 'recharts';
import { apiUrl } from './api';

function ErrorBoundary({ children }) {
  const [error, setError] = React.useState(null);
  if (error) {
    return <div style={{color:'red', background:'#fee', padding:16, border:'1px solid #f00'}}>
      <b>Unexpected error:</b>
      <pre style={{whiteSpace:'pre-wrap'}}>{error.toString()}</pre>
    </div>;
  }
  return (
    <React.Fragment>
      {React.Children.map(children, child => {
        try {
          return child;
        } catch (e) {
          setError(e);
          return null;
        }
      })}
    </React.Fragment>
  );
}

export default function SummaryPage({ onBack }) {
  const [summary, setSummary] = React.useState(null);
  const [error, setError] = React.useState(null);
  const [loading, setLoading] = React.useState(true);
  const [startDate, setStartDate] = React.useState("");
  const [endDate, setEndDate] = React.useState("");

  // Default dates: Jan 1st this year and today
  React.useEffect(() => {
    const now = new Date();
    const yyyy = now.getFullYear();
    const mm = String(now.getMonth() + 1).padStart(2, '0');
    const dd = String(now.getDate()).padStart(2, '0');
    setStartDate(`${yyyy}-01-01 00:00:00`);
    setEndDate(`${yyyy}-${mm}-${dd} 00:00:00`);
  }, []);

  // Fetch summary with current filters
  const fetchSummary = React.useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const strategy = window._lastStrategy || 'cross_sma';
      let url = apiUrl(`/summary/${strategy}?`);
      if (startDate) url += `start_date=${encodeURIComponent(startDate)}&`;
      if (endDate) url += `end_date=${encodeURIComponent(endDate)}&`;
      url = url.replace(/&$/, "");
      const res = await fetch(url);
      if (!res.ok) throw new Error('No summary');
      const data = await res.json();
      window._lastSummary = data;
      setSummary(data);
    } catch (err) {
      setError('Could not fetch summary: ' + err);
    } finally {
      setLoading(false);
    }
  }, [startDate, endDate]);

  React.useEffect(() => {
    fetchSummary();
  }, [fetchSummary]);

  // Debug block
  if (typeof window !== 'undefined') {
    window._summaryError = error;
    window._summaryData = summary;
  }

  return (
    <ErrorBoundary>
      <div className="summary-block">
        <button onClick={onBack} style={{marginBottom: 16}}>Back to Backtest</button>
        <div style={{marginBottom: 16, display: 'flex', gap: 16, alignItems: 'center'}}>
          <label>
            Start date:<br/>
            <input
              type="datetime-local"
              value={startDate}
              onChange={e => setStartDate(e.target.value ? e.target.value.replace('T', ' ') + ':00' : '')}
              style={{fontSize: '1em'}}
            />
          </label>
          <label>
            End date:<br/>
            <input
              type="datetime-local"
              value={endDate}
              onChange={e => setEndDate(e.target.value ? e.target.value.replace('T', ' ') + ':00' : '')}
              style={{fontSize: '1em'}}
            />
          </label>
          <button onClick={fetchSummary} style={{height: 38}}>Filter</button>
        </div>
        {loading && <div>Loading summary...</div>}
        {error && <div style={{color:'red'}}>{error}</div>}
        <textarea
          style={{width:'100%', minHeight:80, fontSize:'0.95em', marginBottom:16, fontFamily:'monospace'}}
          readOnly
          value={summary ? JSON.stringify(summary, null, 2) : 'No summary data.'}
        />
        {!loading && !error && (!summary || Object.keys(summary).length === 0) && (
          <div style={{color:'orange'}}>No summary data available.</div>
        )}
        {!loading && !error && summary && Object.keys(summary).length > 0 && (
          <>
            <h2>Summary cross_sma</h2>
            <ul>
              <li><b>Total trades:</b> {summary.total_trades}</li>
              <li><b>Total profit/loss:</b> {Number(summary.total_profit).toFixed(2)}</li>
              <li><b>Winning trades:</b> {summary.winning_trades}</li>
              <li><b>Losing trades:</b> {summary.losing_trades}</li>
              <li><b>Win rate:</b> {Number(summary.win_rate).toFixed(2)}%</li>
              <li><b>Average profit/loss per trade:</b> {Number(summary.avg_profit).toFixed(2)}</li>
              <li><b>Maximum drawdown:</b> {Number(summary.max_drawdown).toFixed(2)}</li>
            </ul>
            <h3>Equity Curve</h3>
            <ResponsiveContainer width="100%" height={250}>
              <LineChart data={Array.isArray(summary.equity_curve) ? summary.equity_curve.map((v, i) => ({ trade: i+1, equity: v })) : []}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="trade" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="equity" stroke="#8884d8" dot={false} />
              </LineChart>
            </ResponsiveContainer>
            <h3>Drawdown Curve</h3>
            <ResponsiveContainer width="100%" height={250}>
              <LineChart data={Array.isArray(summary.drawdown_curve) ? summary.drawdown_curve.map((v, i) => ({ trade: i+1, drawdown: v })) : []}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="trade" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="drawdown" stroke="#ff4d4f" dot={false} />
              </LineChart>
            </ResponsiveContainer>
            <h3>Trades</h3>
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
                  {Array.isArray(summary.trades) && summary.trades.slice(0, 20).map((t, i) => (
                    <tr key={i}>
                      <td>{t.entry_time}</td>
                      <td>{t.entry_price}</td>
                      <td>{t.exit_time}</td>
                      <td>{t.exit_price}</td>
                      <td style={{color: t.profit >= 0 ? 'green' : 'red'}}>{Number(t.profit).toFixed(2)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
              {Array.isArray(summary.trades) && summary.trades.length > 20 && <div style={{color: '#888', fontSize: '0.9em'}}>Showing first 20 trades...</div>}
            </div>
          </>
        )}
      </div>
    </ErrorBoundary>
  );
}
