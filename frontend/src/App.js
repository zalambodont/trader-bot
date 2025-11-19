import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';
import PairSearch from './components/PairSearch';
import MarketScanner from './components/MarketScanner';
import ActivePositions from './components/ActivePositions';
import { createLoggedAxios, setLoggingEnabled, isLoggingEnabled } from './apiLogger';

// Setup comprehensive API logging
createLoggedAxios(axios);

const API_URL = 'http://localhost:5001';

// Log initialization
console.log('%c═══════════════════════════════════════', 'color: #00ff00; font-weight: bold;');
console.log('%c🚀 CRYPTO TRADING BOT - INITIALIZED', 'color: #00ff00; font-weight: bold; font-size: 16px;');
console.log('%c═══════════════════════════════════════', 'color: #00ff00; font-weight: bold;');
console.log('✅ API Logging: ENABLED');
console.log('✅ AI Analysis Logging: ENABLED');
console.log('✅ Error Logging: ENABLED');
console.log('📡 API URL:', API_URL);
console.log('---');

// Global AI analyses storage for the panel
window.aiAnalyses = [];

function App() {
  const [selectedPairs, setSelectedPairs] = useState([]);
  const [portfolioStats, setPortfolioStats] = useState({
    total_value: 0,
    total_unrealized_pnl: 0,
    total_return: 0,
    positions_count: 0,
    running: false,
    mode: 'paper'
  });
  const [loggingEnabled, setLoggingEnabledState] = useState(false);

  useEffect(() => {
    fetchPortfolioStats();
    const interval = setInterval(fetchPortfolioStats, 5000);
    return () => clearInterval(interval);
  }, []);

  const fetchPortfolioStats = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/multi-bot/status`);
      if (response.data.portfolio) {
        setPortfolioStats({
          total_value: response.data.portfolio.total_value || 0,
          total_unrealized_pnl: response.data.portfolio.total_unrealized_pnl || 0,
          total_return: response.data.portfolio.total_return || 0,
          positions_count: response.data.portfolio.positions?.length || 0,
          running: response.data.running || false,
          mode: response.data.mode || 'paper'
        });
      }
    } catch (error) {
      // Silently fail
    }
  };

  const toggleMode = () => {
    if (portfolioStats.running) {
      alert('Cannot change mode while bot is running. Please stop trading first.');
      return;
    }
    // Mode will be set when starting trading in TradingSettings
    alert('Mode will be set when you start trading. Use the trading settings to choose Paper or Live mode.');
  };

  const toggleLogging = () => {
    const newState = !loggingEnabled;
    setLoggingEnabledState(newState);
    setLoggingEnabled(newState);
  };

  const closeAllPositions = async () => {
    if (!portfolioStats.running) {
      alert('Bot is not running. Please start trading first.');
      return;
    }

    if (portfolioStats.positions_count === 0) {
      alert('No open positions to close.');
      return;
    }

    if (!window.confirm(`Close all ${portfolioStats.positions_count} positions and realize P&L of $${portfolioStats.total_unrealized_pnl.toFixed(2)}?`)) {
      return;
    }

    try {
      const response = await axios.post(`${API_URL}/api/multi-bot/stop`);
      if (response.data.success) {
        alert(`Closed all positions. Final P&L: $${portfolioStats.total_unrealized_pnl.toFixed(2)}`);
        fetchPortfolioStats();
      }
    } catch (error) {
      console.error('Failed to close positions:', error);
      const errorMsg = error.response?.data?.error || error.message || 'Unknown error';
      alert(`Failed to close positions: ${errorMsg}`);
    }
  };

  const handlePairSelect = (symbol) => {
    setSelectedPairs(prev => {
      if (prev.includes(symbol)) {
        return prev.filter(s => s !== symbol);
      } else {
        return [...prev, symbol];
      }
    });
  };

  const getPnLColor = (pnl) => {
    if (pnl > 0) return '#00ff00';
    if (pnl < 0) return '#ff4444';
    return '#888';
  };

  return (
    <div className="App">
      <header className="header">
        <div className="header-left">
          <h1>🚀 Crypto Market Scanner & Trading Bot</h1>
          <span
            className={`mode-badge ${portfolioStats.mode}`}
            onClick={toggleMode}
            title="Click to change mode (only when stopped)"
          >
            {portfolioStats.mode.toUpperCase()} MODE
          </span>
          <div className="toggle-switch-container" title="Console Logging">
            <label className="toggle-switch">
              <input
                type="checkbox"
                checked={loggingEnabled}
                onChange={toggleLogging}
              />
              <span className="toggle-slider"></span>
            </label>
          </div>
        </div>

        {portfolioStats.running && (
          <div className="header-stats">
            <div className="stat-box">
              <span className="stat-label">Portfolio</span>
              <span className="stat-value">${portfolioStats.total_value.toFixed(2)}</span>
            </div>
            <div className="stat-box">
              <span className="stat-label">P&L</span>
              <span className="stat-value" style={{ color: getPnLColor(portfolioStats.total_unrealized_pnl) }}>
                {portfolioStats.total_unrealized_pnl > 0 ? '+' : ''}${portfolioStats.total_unrealized_pnl.toFixed(2)}
                <span className="stat-percent" style={{ color: getPnLColor(portfolioStats.total_return) }}>
                  ({portfolioStats.total_return > 0 ? '+' : ''}{portfolioStats.total_return.toFixed(2)}%)
                </span>
              </span>
            </div>
            <div className="stat-box">
              <span className="stat-label">Positions</span>
              <span className="stat-value">{portfolioStats.positions_count}</span>
            </div>
            <button
              className="close-all-btn"
              onClick={closeAllPositions}
              disabled={portfolioStats.positions_count === 0}
            >
              Close All & Take Profit
            </button>
          </div>
        )}
      </header>

      <div className="dashboard">
        <div className="main-panel-full">
          <PairSearch selectedPairs={selectedPairs} onPairSelect={handlePairSelect} />
          <MarketScanner selectedPairs={selectedPairs} onPairSelect={handlePairSelect} />
          <ActivePositions />
        </div>
      </div>
    </div>
  );
}

export default App;
