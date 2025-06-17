import React, { useState } from 'react';
import './App.css';
import { BrowserRouter as Router, Routes, Route, useNavigate } from 'react-router-dom';
import HomePage from './HomePage';
import SummaryPage from './SummaryPage';
import HistoryManagerPage from './HistoryManagerPage';
import BacktestResultPage from './BacktestResultPage';
import { apiUrl, fetchWithErrorHandling } from './api';
import { LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid, ResponsiveContainer, Legend } from 'recharts';

const STRATEGIES = [
  { label: 'SMA Crossover', value: 'cross_sma' },
  { label: 'EMA Crossover', value: 'cross_ema' },
];

function BacktestPage() {
  const [strategy, setStrategy] = useState('cross_sma');
  const [historyList, setHistoryList] = useState({});
  const [historyOptions, setHistoryOptions] = useState([]);
  const [selectedHistory, setSelectedHistory] = useState(null);
  const [symbol, setSymbol] = useState('');
  const [timeframe, setTimeframe] = useState('');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [csvRows, setCsvRows] = useState(null);
  const [showSummary, setShowSummary] = useState(false);
  const [showError, setShowError] = useState(true);
  const navigate = useNavigate();

  // Fetch history list on mount or when strategy changes
  React.useEffect(() => {
    async function fetchHistoryList() {
      setLoading(true);
      setError(null);
      try {
        const res = await fetch(apiUrl('/api/history/list'));
        const data = await res.json();
        setHistoryList(data);
        // Flatten and filter options for the selected strategy
        let options = [];
        Object.entries(data).forEach(([symbol, tfs]) => {
          Object.entries(tfs).forEach(([tf, meta]) => {
            options.push({
              symbol,
              timeframe: tf,
              ...meta
            });
          });
        });
        setHistoryOptions(options);
        if (options.length > 0) {
          setSelectedHistory(options[0]);
        } else {
          setSelectedHistory(null);
        }
      } catch (e) {
        setError('Error loading historical data');
      } finally {
        setLoading(false);
      }
    }
    fetchHistoryList();
  }, [strategy]);

  // Update fields when selectedHistory changes
  React.useEffect(() => {
    if (selectedHistory) {
      setSymbol(selectedHistory.symbol);
      setTimeframe(selectedHistory.timeframe);
      setStartDate(selectedHistory.min_date?.slice(0, 10) || '');
      setEndDate(selectedHistory.max_date?.slice(0, 10) || '');
    } else {
      setSymbol('');
      setTimeframe('');
      setStartDate('');
      setEndDate('');
    }
  }, [selectedHistory]);

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
    try {
      const body = {
        strategy,
        symbol: selectedHistory.symbol,
        timeframe: selectedHistory.timeframe,
        filename: selectedHistory.filename, // Pass the exact file
        start_date,
        end_date
      };
      const data = await fetchWithErrorHandling(apiUrl('/api/backtest/'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
      });
      if (data.success) {
        navigate('/backtest/result', {
          state: {
            summary: data.summary || null,
            rawStdout: data.stdout || 'No summary available',
            strategy,
            historyFile: data.result_file || ''
          }
        });
        return;
      } else {
        setError(data.error || 'Unknown error');
      }
    } catch (err) {
      setError(err.message || 'Error connecting to backend');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app-container">
      {error && showError && (
        <div className="error" style={{position:'relative', paddingRight:32, marginBottom:16}}>
          <span>Error: {error}</span>
          <button onClick={() => setShowError(false)} style={{position:'absolute', right:8, top:8, background:'none', border:'none', fontSize:'1.2em', cursor:'pointer'}}>&times;</button>
        </div>
      )}
      <h1>Crypto Bot Backtesting</h1>
      <form className="backtest-form" onSubmit={handleSubmit}>
        <label>
          Strategy:
          <select value={strategy} onChange={e => setStrategy(e.target.value)}>
            {STRATEGIES.map(s => (
              <option key={s.value} value={s.value}>{s.label}</option>
            ))}
          </select>
        </label>
        {historyOptions.length > 0 ? (
          <label>
            Historical Data:
            <select value={selectedHistory ? `${selectedHistory.symbol}|${selectedHistory.timeframe}` : ''}
              onChange={e => {
                const [sym, tf] = e.target.value.split('|');
                const found = historyOptions.find(opt => opt.symbol === sym && opt.timeframe === tf);
                setSelectedHistory(found);
              }}>
              {historyOptions.map(opt => (
                <option key={opt.symbol + '|' + opt.timeframe} value={opt.symbol + '|' + opt.timeframe}>
                  {opt.symbol} - {opt.timeframe} ({opt.min_date?.slice(0,10)} to {opt.max_date?.slice(0,10)})
                </option>
              ))}
            </select>
          </label>
        ) : (
          <div style={{color: 'red', margin: '16px 0'}}>No historical data available for backtesting. Please generate data first.</div>
        )}
        {/* Group symbol and timeframe in one row */}
        <div style={{ display: 'flex', gap: 16, marginBottom: 8 }}>
          <div style={{ flex: 1 }}>
            <label style={{ display: 'block' }}>Symbol:
              <input value={symbol} disabled style={{ background: '#f5f5f5', width: '100%' }} />
            </label>
          </div>
          <div style={{ flex: 1 }}>
            <label style={{ display: 'block' }}>Timeframe:
              <input value={timeframe} disabled style={{ background: '#f5f5f5', width: '100%' }} />
            </label>
          </div>
        </div>
        {/* Group dates in one row */}
        <div style={{ display: 'flex', gap: 16, marginBottom: 8 }}>
          <div style={{ flex: 1 }}>
            <label style={{ display: 'block' }}>Start date:
              <input type="date" value={startDate} disabled style={{ background: '#f5f5f5', width: '100%' }} />
            </label>
          </div>
          <div style={{ flex: 1 }}>
            <label style={{ display: 'block' }}>End date:
              <input type="date" value={endDate} disabled style={{ background: '#f5f5f5', width: '100%' }} />
            </label>
          </div>
        </div>
        {historyOptions.length > 0 && (
          <style>{`
            .backtest-form select { background: #fff !important; }
          `}</style>
        )}
        <button type="submit" disabled={loading || !selectedHistory}>{loading ? 'Running...' : 'Run Backtest'}</button>
      </form>
    </div>
  );
}

function TopNav() {
  const navigate = useNavigate();
  return (
    <nav className="top-nav">
      <button onClick={() => navigate('/')}>Home</button>
      <button onClick={() => navigate('/backtest')}>Backtest</button>
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
          <Route path="/backtest/result" element={<BacktestResultPage />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
