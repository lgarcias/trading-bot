import React, { useEffect, useState } from "react";
import { apiUrl } from "./api";

function HistoryManagerPage() {
  const [historyList, setHistoryList] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [form, setForm] = useState({
    symbol: "BTC/USDT",
    timeframe: "1d",
    start_date: "",
    end_date: ""
  });
  const [downloading, setDownloading] = useState(false);
  const [actionMsg, setActionMsg] = useState("");

  const fetchHistory = () => {
    setLoading(true);
    fetch(apiUrl("/history/list"))
      .then((res) => res.json())
      .then((data) => {
        setHistoryList(data);
        setLoading(false);
      })
      .catch(() => {
        setError("Error loading history list");
        setLoading(false);
      });
  };

  useEffect(() => {
    fetchHistory();
  }, []);

  useEffect(() => {
    if (downloading) {
      document.body.style.cursor = 'wait';
    } else {
      document.body.style.cursor = '';
    }
    return () => { document.body.style.cursor = ''; };
  }, [downloading]);

  const handleInputChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleDownload = async (e) => {
    e.preventDefault();
    setDownloading(true);
    setActionMsg("");
    setError(null);
    try {
      const res = await fetch(apiUrl("/history/download"), {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(form)
      });
      const data = await res.json();
      if (data.success) {
        setActionMsg("Historical downloaded successfully.");
        fetchHistory();
      } else {
        setError(data.error || "Download failed");
      }
    } catch (err) {
      setError("Error downloading historical");
    }
    setDownloading(false);
  };

  const handleDelete = async (symbol, timeframe) => {
    setActionMsg("");
    setError(null);
    try {
      // Codifica el símbolo para la URL (BTC/USDT -> BTC%2FUSDT)
      const res = await fetch(apiUrl(`/history/${encodeURIComponent(symbol)}/${timeframe}`), { method: "DELETE" });
      const data = await res.json();
      if (data.success) {
        setActionMsg("Historical deleted.");
        fetchHistory();
      } else {
        setError(data.error || "Delete failed");
        // Si el error es que no existe, forzar refresco de la tabla
        if (data.error && data.error.includes('not found')) {
          fetchHistory();
        }
      }
    } catch (err) {
      setError("Error deleting historical");
    }
  };

  return (
    <div className="history-manager-page">
      <h2>Historical Data Manager</h2>
      {loading && <p>Loading...</p>}
      {error && <p style={{ color: "red" }}>{error}</p>}
      {actionMsg && <p style={{ color: "green" }}>{actionMsg}</p>}
      {/* Download form */}
      <form onSubmit={handleDownload} style={{ marginBottom: 24 }}>
        <label>
          Symbol:
          <input name="symbol" value={form.symbol} onChange={handleInputChange} required />
        </label>
        <label>
          Timeframe:
          <input name="timeframe" value={form.timeframe} onChange={handleInputChange} required />
        </label>
        <label>
          Start Date:
          <input name="start_date" type="date" value={form.start_date} onChange={handleInputChange} required />
        </label>
        <label>
          End Date:
          <input name="end_date" type="date" value={form.end_date} onChange={handleInputChange} required />
        </label>
        <button type="submit" disabled={downloading}>{downloading ? "Downloading..." : "Download"}</button>
      </form>
      {/* Table of available historicals */}
      <table>
        <thead>
          <tr>
            <th>Symbol</th>
            <th>Timeframe</th>
            <th>Min Date</th>
            <th>Max Date</th>
            <th>File</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {Object.entries(historyList).length === 0 && !loading ? (
            <tr><td colSpan={6}>No historicals found.</td></tr>
          ) : (
            Object.entries(historyList).map(([symbol, timeframes]) =>
              Object.entries(timeframes).map(([tf, meta]) => (
                <tr key={symbol + tf}>
                  <td>{symbol}</td>
                  <td>{tf}</td>
                  <td>{meta.min_date}</td>
                  <td>{meta.max_date}</td>
                  <td>{meta.filename}</td>
                  <td>
                    <button onClick={() => handleDelete(symbol, tf)}>Delete</button>
                  </td>
                </tr>
              ))
            )
          )}
        </tbody>
      </table>
    </div>
  );
}

export default HistoryManagerPage;
