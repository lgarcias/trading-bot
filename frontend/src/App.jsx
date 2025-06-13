import React, { useState } from 'react';
import './App.css';
import SummaryPage from './SummaryPage';
import { LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid, ResponsiveContainer, Legend } from 'recharts';

const STRATEGIES = [
  { label: 'SMA Crossover', value: 'cross_sma' },
  { label: 'EMA Crossover', value: 'cross_ema' },
];

function App() {
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

  // Obtener fechas por defecto: 1 de enero de este año y hoy
  React.useEffect(() => {
    const now = new Date();
    const yyyy = now.getFullYear();
    const mm = String(now.getMonth() + 1).padStart(2, '0');
    const dd = String(now.getDate()).padStart(2, '0');
    setStartDate(`${yyyy}-01-01`);
    setEndDate(`${yyyy}-${mm}-${dd}`);
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    // Validar fechas
    if (!startDate || !endDate) {
      setError('Debes seleccionar fecha de inicio y fin.');
      return;
    }
    setLoading(true);
    setResult(null);
    setCsvRows(null);
    // Formatear fechas a 'YYYY-MM-DD 00:00:00'
    const start_date = startDate.length === 10 ? startDate + ' 00:00:00' : startDate;
    const end_date = endDate.length === 10 ? endDate + ' 00:00:00' : endDate;
    try {
      const body = { strategy, symbol, timeframe, start_date, end_date };
      const res = await fetch('http://localhost:8000/backtest/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
      });
      const data = await res.json();
      if (data.success) {
        setResult(data);
        setLastStrategy(strategy);
        window._lastStrategy = strategy;
        setShowSummary(true);
      } else if (data.error && data.error.includes('No historical data')) {
        if (window.confirm('No hay datos históricos para ese periodo. ¿Quieres descargarlos del exchange?')) {
          const downloadRes = await fetch('http://localhost:8000/download_history/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body)
          });
          const downloadData = await downloadRes.json();
          if (downloadData.success) {
            await handleSubmit(e);
            return;
          } else {
            setError(downloadData.error || 'Error al descargar datos históricos');
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
      <h1>Crypto Bot Backtesting</h1>
      <form onSubmit={handleSubmit} className="backtest-form">
        <label>
          Estrategia:
          <select value={strategy} onChange={e => setStrategy(e.target.value)}>
            {STRATEGIES.map(s => (
              <option key={s.value} value={s.value}>{s.label}</option>
            ))}
          </select>
        </label>
        <label>
          Símbolo:
          <input value={symbol} onChange={e => setSymbol(e.target.value)} />
        </label>
        <label>
          Timeframe:
          <input value={timeframe} onChange={e => setTimeframe(e.target.value)} />
        </label>
        <label>
          Fecha inicio:
          <input type="date" value={startDate} onChange={e => setStartDate(e.target.value)} />
        </label>
        <label>
          Fecha fin:
          <input type="date" value={endDate} onChange={e => setEndDate(e.target.value)} />
        </label>
        <button type="submit" disabled={loading}>{loading ? 'Ejecutando...' : 'Ejecutar Backtest'}</button>
      </form>
      {error && <div className="error">Error: {error}</div>}
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

export default App;
