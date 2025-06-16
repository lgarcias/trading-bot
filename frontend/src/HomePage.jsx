import React from "react";
import { apiUrl } from "./api";
import { useNavigate } from "react-router-dom";

export default function HomePage() {
  const navigate = useNavigate();
  return (
    <div className="home-container">
      <h1>Crypto Bot Trading App</h1>
      <p>Welcome! Start a new backtest or explore your results.</p>
      <button onClick={() => navigate('/backtest')} style={{ marginTop: 32, fontSize: "1.2em" }}>
        Go to Backtest
      </button>
    </div>
  );
}
