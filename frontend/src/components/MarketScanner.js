import React, { useState, useEffect } from 'react';
import axios from 'axios';
import TradingSettings from './TradingSettings';
import './MarketScanner.css';

const API_URL = 'http://localhost:5001';

function MarketScanner({ selectedPairs, onPairSelect }) {
  const [scanning, setScanning] = useState(false);
  const [opportunities, setOpportunities] = useState([]);
  const [minScore, setMinScore] = useState(65);
  const [lastScan, setLastScan] = useState(null);
  const [botRunning, setBotRunning] = useState(false);
  const [showSettings, setShowSettings] = useState(false);

  const scanMarket = async () => {
    setScanning(true);
    try {
      const response = await axios.post(`${API_URL}/api/scanner/scan`, {
        min_score: minScore
      });

      if (response.data.success) {
        setOpportunities(response.data.opportunities);
        setLastScan(new Date());
      }
    } catch (error) {
      console.error('Scan failed:', error);
    } finally {
      setScanning(false);
    }
  };

  const getOpportunities = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/scanner/opportunities?limit=20`);
      setOpportunities(response.data.opportunities);
    } catch (error) {
      console.error('Failed to get opportunities:', error);
    }
  };

  useEffect(() => {
    getOpportunities();
    checkBotStatus();
    // Refresh opportunities every 30 seconds
    const interval = setInterval(() => {
      getOpportunities();
      checkBotStatus();
    }, 30000);
    return () => clearInterval(interval);
  }, []);

  const checkBotStatus = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/multi-bot/status`);
      setBotRunning(response.data.running);
    } catch (error) {
      console.error('Failed to check bot status:', error);
    }
  };

  const togglePairSelection = (symbol) => {
    onPairSelect(symbol);
  };

  const selectAll = () => {
    opportunities.forEach(opp => {
      if (!selectedPairs.includes(opp.symbol)) {
        onPairSelect(opp.symbol);
      }
    });
  };

  const clearSelection = () => {
    selectedPairs.forEach(pair => onPairSelect(pair));
  };

  const startTradingSelected = () => {
    if (selectedPairs.length === 0) {
      alert('Please select at least one pair to trade');
      return;
    }
    setShowSettings(true);
  };

  const handleStartTrading = async (settings) => {
    try {
      const response = await axios.post(`${API_URL}/api/multi-bot/start`, {
        quote_currency: 'USDT',
        min_volume: 500000,
        max_pairs: 100,
        initial_balance: settings.totalCapital,
        max_positions: settings.maxPositions,
        max_allocation: settings.totalCapital / settings.maxPositions / settings.totalCapital,
        scan_interval: settings.scanInterval,
        min_score: settings.minScore,
        mode: settings.tradingMode,
        timeframe: '15m',
        stop_loss_pct: settings.stopLossPct / 100,
        take_profit_pct: settings.takeProfitPct / 100,
        selected_pairs: selectedPairs
      });

      if (response.data.success) {
        setBotRunning(true);
        alert(`Started trading ${selectedPairs.length} pairs with $${settings.totalCapital} total capital`);
      }
    } catch (error) {
      console.error('Failed to start bot:', error);
      alert('Failed to start trading: ' + error.message);
    }
  };

  const stopTrading = async () => {
    try {
      await axios.post(`${API_URL}/api/multi-bot/stop`);
      setBotRunning(false);
      alert('Trading stopped');
    } catch (error) {
      console.error('Failed to stop bot:', error);
      alert('Failed to stop trading');
    }
  };

  const getScoreColor = (score) => {
    if (score >= 80) return '#00ff00';
    if (score >= 70) return '#7fff00';
    if (score >= 60) return '#ffff00';
    return '#ff9900';
  };

  const getDirectionColor = (direction) => {
    if (direction === 'LONG') return '#00ff00';
    if (direction === 'SHORT') return '#ff4444';
    return '#888';
  };

  return (
    <div className="market-scanner">
      <div className="scanner-header">
        <h2>📊 Market Scanner</h2>
        <div className="scanner-controls">
          <div className="control-group">
            <label>Min Score:</label>
            <input
              type="number"
              value={minScore}
              onChange={(e) => setMinScore(parseInt(e.target.value))}
              min="0"
              max="100"
            />
          </div>
          <button
            onClick={scanMarket}
            disabled={scanning}
            className="scan-button"
          >
            {scanning ? 'Scanning...' : 'Scan Market'}
          </button>
        </div>
      </div>

      {opportunities.length > 0 && (
        <div className="selection-controls">
          <div className="selection-info">
            {selectedPairs.length > 0 ? (
              <span>{selectedPairs.length} pair{selectedPairs.length !== 1 ? 's' : ''} selected</span>
            ) : (
              <span>Click cards to select pairs</span>
            )}
          </div>
          <div className="selection-buttons">
            <button onClick={selectAll} className="select-btn">Select All</button>
            <button onClick={clearSelection} className="select-btn">Clear</button>
            {botRunning ? (
              <button onClick={stopTrading} className="stop-trading-btn">
                Stop Trading
              </button>
            ) : (
              <button
                onClick={startTradingSelected}
                disabled={selectedPairs.length === 0}
                className="start-trading-btn"
              >
                Configure & Trade ({selectedPairs.length})
              </button>
            )}
          </div>
        </div>
      )}

      {lastScan && (
        <div className="scan-info">
          Last scan: {lastScan.toLocaleTimeString()} |
          Found {opportunities.length} opportunities
        </div>
      )}

      <div className="opportunities-grid">
        {opportunities.length === 0 ? (
          <div className="no-opportunities">
            No opportunities found. Try lowering the minimum score or click "Scan Market".
          </div>
        ) : (
          opportunities.map((opp, index) => {
            const isSelected = selectedPairs.includes(opp.symbol);
            return (
              <div
                key={index}
                className={`opportunity-card ${isSelected ? 'selected' : ''}`}
                onClick={() => togglePairSelection(opp.symbol)}
              >
                <div className="opp-header">
                  <div className="opp-symbol-wrapper">
                    <input
                      type="checkbox"
                      checked={isSelected}
                      onChange={() => {}}
                      className="pair-checkbox"
                    />
                    <span className="opp-symbol">{opp.symbol}</span>
                  </div>
                  <span
                    className="opp-score"
                    style={{ color: getScoreColor(opp.score) }}
                  >
                    {opp.score}/100
                  </span>
                </div>

              <div className="opp-details">
                <div className="opp-row">
                  <span>Direction:</span>
                  <strong style={{ color: getDirectionColor(opp.direction) }}>
                    {opp.direction || 'NEUTRAL'}
                  </strong>
                </div>
                <div className="opp-row">
                  <span>Price:</span>
                  <strong>${opp.price.toFixed(8)}</strong>
                </div>
                <div className="opp-row">
                  <span>RSI:</span>
                  <strong style={{
                    color: opp.rsi < 30 ? '#00ff00' :
                           opp.rsi > 70 ? '#ff4444' : '#fff'
                  }}>
                    {opp.rsi.toFixed(1)}
                  </strong>
                </div>
                <div className="opp-row">
                  <span>24h Volume:</span>
                  <strong>${(opp.volume_24h / 1000000).toFixed(2)}M</strong>
                </div>
                <div className="opp-row">
                  <span>Volatility:</span>
                  <strong>{opp.volatility.toFixed(2)}%</strong>
                </div>
              </div>

              <div className="opp-signals">
                {opp.signals && opp.signals.map((signal, i) => (
                  <span key={i} className="signal-tag">{signal}</span>
                ))}
              </div>
            </div>
          );
          })
        )}
      </div>

      <TradingSettings
        isOpen={showSettings}
        onClose={() => setShowSettings(false)}
        onStart={handleStartTrading}
      />
    </div>
  );
}

export default MarketScanner;
