import React, { useState } from 'react';
import './App.css';
import { BrowserRouter as Router, Routes, Route, useNavigate } from 'react-router-dom';
import HomePage from './HomePage';
import SummaryPage from './SummaryPage';
import HistoryManagerPage from './HistoryManagerPage';
import { apiUrl } from './api';
import { LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid, ResponsiveContainer, Legend } from 'recharts';

const STRATEGIES = [
  { label: 'SMA Crossover', value: 'cross_sma' },
  { label: 'EMA Crossover', value: 'cross_ema' },
];

function BacktestPage() {
  const [strategy, setStrategy] = useState('cross_sma');
  const [symbol, setSymbol] = useState('BTC/USDT');
  const [timeframe, setTimeframe] = useState('1m');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [csvRows, setCsvRows] = useState(null);
  const [showSummary, setShowSummary] = useState(false);
  const [lastStrategy, setLastStrategy] = useState('cross_sma');
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [showError, setShowError] = useState(true);
  const [historyRange, setHistoryRange] = useState(null);
  const navigate = useNavigate();

  // Al cargar el formulario, obtener el rango de fechas del histórico local
  React.useEffect(() => {
    async function fetchHistoryRange() {
      try {
        const url = `${apiUrl}/history_range/?strategy=${strategy}&symbol=${encodeURIComponent(symbol)}&timeframe=${timeframe}`;
        const res = await fetch(url);
        const data = await res.json();
        if (data.success) {
          setHistoryRange({ start: data.start_date, end: data.end_date });
          setStartDate(data.start_date);
          setEndDate(data.end_date);
        } else {
          setHistoryRange(null);
          setStartDate("");
          setEndDate("");
        }
      } catch (e) {
        setHistoryRange(null);
        setStartDate("");
        setEndDate("");
      }
    }
    fetchHistoryRange();
  }, [strategy, symbol, timeframe]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setShowError(true);
    // Validar fechas
    if (!startDate || !endDate) {
      setError('You must select start and end date.');
      return;
    }
    setLoading(true);
    setResult(null);
    setCsvRows(null);
    // Usar solo la parte de fecha (YYYY-MM-DD)
    const start_date = startDate.slice(0, 10);
    const end_date = endDate.slice(0, 10);
    // Comprobar si el rango solicitado está cubierto por el histórico local
    if (historyRange) {
      const histStart = historyRange.start.slice(0, 10);
      const histEnd = historyRange.end.slice(0, 10);
      if (start_date < histStart || end_date > histEnd) {
        if (!window.confirm('The selected date range is not available locally. Download new historical data?')) {
          setLoading(false);
          return;
        }
        // Descargar nuevos datos históricos
        const body = { strategy, symbol, timeframe, start_date, end_date };
        const downloadRes = await fetch(apiUrl('/download_history/'), {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(body)
        });
        const downloadData = await downloadRes.json();
        if (!downloadData.success) {
          setError(downloadData.error || 'Error downloading historical data');
          setLoading(false);
          return;
        }
        // Actualizar el rango local tras descargar
        setHistoryRange({ start: start_date, end: end_date });
      }
    }
    try {
      const body = { strategy, symbol, timeframe, start_date, end_date };
      const res = await fetch(apiUrl('/backtest/'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
      });
      if (res.status === 422) {
        const data = await res.json();
        if (data.detail && Array.isArray(data.detail)) {
          setError(data.detail.map(d => d.msg).join(' | '));
        } else {
          setError('Validation error');
        }
        return;
      }
      const data = await res.json();
      if (data.success) {
        setResult(data);
        setLastStrategy(strategy);
        window._lastStrategy = strategy;
        setShowSummary(true);
      } else if (data.error && data.error.includes('No historical data')) {
        if (window.confirm('No historical data for this period. Download from exchange?')) {
          const downloadRes = await fetch(apiUrl('/download_history/'), {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body)
          });
          const downloadData = await downloadRes.json();
          if (downloadData.success) {
            await handleSubmit(e);
            return;
          } else {
            setError(downloadData.error || 'Error downloading historical data');
          }
        }
      } else {
        setError(data.error || 'Unknown error');
      }
    } catch (err) {
      setError('Error connecting to backend');
    } finally {
      setLoading(false);
    }
  };

  if (showSummary) {
    return <SummaryPage onBack={() => setShowSummary(false)} />;
  }

  return (
    <div className="app-container">
      {error && showError && (
        <div className="error" style={{position:'relative', paddingRight:32, marginBottom:16}}>
          <span>Error: {error}</span>
          <button onClick={() => setShowError(false)} style={{position:'absolute', right:8, top:8, background:'none', border:'none', fontSize:'1.2em', cursor:'pointer'}}>&times;</button>
        </div>
      )}
      <h1>Crypto Bot Backtesting</h1>
      <form onSubmit={handleSubmit} className="backtest-form">
        <label>
          Strategy:
          <select value={strategy} onChange={e => setStrategy(e.target.value)}>
            {STRATEGIES.map(s => (
              <option key={s.value} value={s.value}>{s.label}</option>
            ))}
          </select>
        </label>
        <label>
          Symbol:
          <input value={symbol} onChange={e => setSymbol(e.target.value)} />
        </label>
        <label>
          Timeframe:
          <input value={timeframe} onChange={e => setTimeframe(e.target.value)} />
        </label>
        <label>
          Start date:
          <input type="date" value={startDate} onChange={e => setStartDate(e.target.value)} />
        </label>
        <label>
          End date:
          <input type="date" value={endDate} onChange={e => setEndDate(e.target.value)} />
        </label>
        <button type="submit" disabled={loading || !startDate || !endDate}>{loading ? 'Running...' : 'Run Backtest'}</button>
      </form>
      <button style={{marginTop: 16}} onClick={() => navigate('/')}>Volver a Inicio</button>
      {result && (
        <div className="result">
          <h2>Resultado</h2>
          <p><b>Archivo generado:</b> {result.result_file}</p>
          <pre style={{maxHeight: 300, overflow: 'auto'}}>{result.stdout}</pre>
          {csvRows && (
            <div style={{overflowX: 'auto', marginTop: 16}}>
              <h3>Vista previa del CSV</h3>
              <table style={{width: '100%', fontSize: '0.95em', borderCollapse: 'collapse'}}>
                <thead>
                  <tr>
                    {csvRows[0].map((col, i) => <th key={i} style={{borderBottom: '1px solid #ccc', textAlign: 'left', padding: 4}}>{col}</th>)}
                  </tr>
                </thead>
                <tbody>
                  {csvRows.slice(1, 21).map((row, i) => (
                    <tr key={i}>
                      {row.map((cell, j) => <td key={j} style={{padding: 4, borderBottom: '1px solid #eee'}}>{cell}</td>)}
                    </tr>
                  ))}
                </tbody>
              </table>
              {csvRows.length > 21 && <div style={{color: '#888', fontSize: '0.9em'}}>Mostrando primeras 20 filas...</div>}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

function TopNav() {
  const navigate = useNavigate();
  return (
    <nav className="top-nav">
      <button onClick={() => navigate('/')}>Home</button>
      <button onClick={() => navigate('/summary')}>Summary</button>
      <button onClick={() => navigate('/history')}>Historical Data</button>
    </nav>
  );
}

function App() {
  return (
    <Router>
      <div className="app-container">
        <TopNav />
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/summary" element={<SummaryPage />} />
          <Route path="/history" element={<HistoryManagerPage />} />
          <Route path="/backtest" element={<BacktestPage />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
