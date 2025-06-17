import React, { useEffect, useState } from "react";
import { apiUrl } from "./api";

function HistoryManagerPage() {
  // State variables
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
  const [pendingExtend, setPendingExtend] = useState(null);

  // Fetch the list of available historicals
  const fetchHistory = () => {
    setLoading(true);
    fetch(apiUrl("/api/history/list"))
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

  // Show wait cursor while downloading
  useEffect(() => {
    if (downloading) {
      document.body.style.cursor = 'wait';
    } else {
      document.body.style.cursor = '';
    }
    return () => { document.body.style.cursor = ''; };
  }, [downloading]);

  // Handle form input changes
  const handleInputChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  // Handle download request, including force-extend logic
  const handleDownload = async (e, overrideExtend = false, suggested = null) => {
    e && e.preventDefault();
    setDownloading(true);
    setActionMsg("");
    setError(null);
    setPendingExtend(null);
    let body = { ...form };
    if (overrideExtend && suggested) {
      body = {
        ...body,
        start_date: suggested.suggested_start_date.split("T")[0],
        end_date: suggested.suggested_end_date.split("T")[0],
        force_extend: true
      };
    }
    try {
      const res = await fetch(apiUrl("/api/history/download"), {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body)
      });
      const data = await res.json();
      if (data.success) {
        setActionMsg("Historical data downloaded successfully.");
        fetchHistory();
      } else if (data.force_extend_param) {
        // Show suggestion to extend the range
        setPendingExtend(data);
        setError(
          <span>
            {data.error}<br />
            <b>Current range:</b> {data.current_min_date} to {data.current_max_date}<br />
            <b>Suggested range:</b> {data.suggested_start_date} to {data.suggested_end_date}<br />
            Do you want to extend the download to cover the full range without gaps?
            <br />
            <button onClick={() => handleDownload(null, true, data)} disabled={downloading}>Yes, extend and download</button>
            <button onClick={() => setPendingExtend(null)} disabled={downloading}>No, cancel</button>
          </span>
        );
      } else {
        setError(data.error || "Download failed");
      }
    } catch (err) {
      setError("Error downloading historical data");
    }
    setDownloading(false);
  };

  // Handle delete request
  const handleDelete = async (symbol, timeframe) => {
    setActionMsg("");
    setError(null);
    try {
      // Encode symbol for URL (BTC/USDT -> BTC%2FUSDT)
      const res = await fetch(apiUrl(`/api/history/${encodeURIComponent(symbol)}/${timeframe}`), { method: "DELETE" });
      const data = await res.json();
      if (data.success) {
        setActionMsg("Historical data deleted.");
        fetchHistory();
      } else {
        setError(data.error || "Delete failed");
        // If not found, force table refresh
        if (data.error && data.error.includes('not found')) {
          fetchHistory();
        }
      }
    } catch (err) {
      setError("Error deleting historical data");
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
      {pendingExtend && (
        <div className="extend-suggestion" style={{ marginTop: 24, padding: 16, border: '1px solid #ccc', borderRadius: 4 }}>
          <p><strong>Suggested range extension:</strong></p>
          <p>{pendingExtend.suggested_start_date} to {pendingExtend.suggested_end_date}</p>
          <button onClick={() => handleDownload(null, true, pendingExtend)} disabled={downloading}>Accept extension</button>
          <button onClick={() => setPendingExtend(null)} disabled={downloading}>Cancel</button>
        </div>
      )}
    </div>
  );
}

export default HistoryManagerPage;
