import React, { useState, useEffect } from 'react';
import axios from 'axios';
import TradingSettings from './TradingSettings';
import './MarketScanner.css';
import { logAIAnalysis, logWarning } from '../apiLogger';

const API_URL = 'http://localhost:5001';

function MarketScanner({ selectedPairs, onPairSelect }) {
  const [scanning, setScanning] = useState(false);
  const [opportunities, setOpportunities] = useState([]);
  const [minScore, setMinScore] = useState(65);
  const [lastScan, setLastScan] = useState(null);
  const [botRunning, setBotRunning] = useState(false);
  const [showSettings, setShowSettings] = useState(false);
  const [isScannerCollapsed, setIsScannerCollapsed] = useState(false);
  const [singlePairToTrade, setSinglePairToTrade] = useState(null);

  const scanMarket = async () => {
    setScanning(true);
    try {
      const response = await axios.post(`${API_URL}/api/scanner/scan`, {
        min_score: minScore
      });

      if (response.data.success) {
        const opportunities = response.data.opportunities || [];

        console.log(`%c📊 MARKET SCAN COMPLETE`, 'color: #ffaa00; font-weight: bold; font-size: 14px;');
        console.log(`Found ${opportunities.length} opportunities with min score ${minScore}`);

        // Log AI analysis for each opportunity and auto-select if AI recommends trading
        let aiCount = 0;
        let autoSelectedCount = 0;
        opportunities.forEach(opp => {
          if (opp.ai_analysis) {
            aiCount++;
            logAIAnalysis(opp.ai_analysis, `Market Scanner - ${opp.symbol}`);

            // Auto-select pairs where AI recommends trading
            if (opp.ai_analysis.should_trade && !selectedPairs.includes(opp.symbol)) {
              onPairSelect(opp.symbol);
              autoSelectedCount++;
            }
          }
        });

        if (aiCount === 0) {
          logWarning('No AI analysis found in market scan results', {
            totalOpportunities: opportunities.length,
            minScore: minScore
          });
        } else {
          console.log(`%c✅ AI Analysis received for ${aiCount}/${opportunities.length} opportunities`,
            'color: #00ff00; font-weight: bold;');
          if (autoSelectedCount > 0) {
            console.log(`%c🤖 Auto-selected ${autoSelectedCount} pairs based on AI recommendation`,
              'color: #00ff00; font-weight: bold;');
          }
        }

        setOpportunities(opportunities);
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
      const opportunities = response.data.opportunities || [];

      // Log AI analysis if present and auto-select if AI recommends trading
      let autoSelectedCount = 0;
      opportunities.forEach(opp => {
        if (opp.ai_analysis) {
          logAIAnalysis(opp.ai_analysis, `Auto-refresh - ${opp.symbol}`);

          // Auto-select pairs where AI recommends trading (only on first discovery)
          if (opp.ai_analysis.should_trade && !selectedPairs.includes(opp.symbol)) {
            onPairSelect(opp.symbol);
            autoSelectedCount++;
          }
        }
      });

      if (autoSelectedCount > 0) {
        console.log(`%c🤖 Auto-selected ${autoSelectedCount} new pairs based on AI recommendation`,
          'color: #00ff00; font-weight: bold;');
      }

      setOpportunities(opportunities);
    } catch (error) {
      console.error('Failed to get opportunities:', error);
    }
  };

  useEffect(() => {
    getOpportunities();
    checkBotStatus();
    // Auto-refresh disabled - user must manually scan
    // const interval = setInterval(() => {
    //   getOpportunities();
    //   checkBotStatus();
    // }, 30000);
    // return () => clearInterval(interval);
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
    setSinglePairToTrade(null);
    setShowSettings(true);
  };

  const startTradingSinglePair = (pairSymbol) => {
    setSinglePairToTrade(pairSymbol);
    setShowSettings(true);
  };

  const handleStartTrading = async (settings) => {
    try {
      // Determine which pairs to trade
      const pairsToTrade = singlePairToTrade ? [singlePairToTrade] : selectedPairs;

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
        selected_pairs: pairsToTrade
      });

      if (response.data.success) {
        setBotRunning(true);
        setShowSettings(false);
        setSinglePairToTrade(null);
        alert(`Started trading ${pairsToTrade.length} pair${pairsToTrade.length !== 1 ? 's' : ''} with $${settings.totalCapital} total capital`);
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

  const toggleScannerAccordion = (event) => {
    if (event && event.target.closest('button')) {
      return;
    }
    setIsScannerCollapsed(prev => !prev);
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

          <span className="accordion-toggle-icon" aria-hidden="true" onClick={toggleScannerAccordion}>
            {isScannerCollapsed ? 'Expand' : 'Collapse'}
          </span>
        </div>
        
      </div>

      {opportunities.length > 0 && (
        <div
          className={`selection-controls`}
          
        >
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

      {lastScan && !isScannerCollapsed && (
        <div className="scan-info">
          Last scan: {lastScan.toLocaleTimeString()} |
          Found {opportunities.length} opportunities
        </div>
      )}

      <div
        className={`opportunities-grid ${isScannerCollapsed ? 'collapsed' : ''}`}
        aria-hidden={isScannerCollapsed}
      >
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

              {opp.ai_analysis && (
                <div className="ai-analysis-inline">
                  <div className="ai-header">🤖 AI Analysis</div>
                  <div className="ai-metrics">
                    <div className="ai-metric">
                      <span className="ai-label">Decision:</span>
                      <span
                        className="ai-value"
                        style={{ color: opp.ai_analysis.should_trade ? '#00ff00' : '#ff4444' }}
                      >
                        {opp.ai_analysis.should_trade ? '✅ TRADE' : '❌ SKIP'}
                      </span>
                    </div>
                    <div className="ai-metric">
                      <span className="ai-label">Confidence:</span>
                      <span
                        className="ai-value"
                        style={{
                          color: opp.ai_analysis.confidence >= 0.7 ? '#00ff00' :
                                 opp.ai_analysis.confidence >= 0.5 ? '#ffaa00' : '#ff4444'
                        }}
                      >
                        {(opp.ai_analysis.confidence * 100).toFixed(0)}%
                      </span>
                    </div>
                    <div className="ai-metric">
                      <span className="ai-label">Risk:</span>
                      <span
                        className="ai-value"
                        style={{
                          color: opp.ai_analysis.risk_assessment === 'low' ? '#00ff00' :
                                 opp.ai_analysis.risk_assessment === 'medium' ? '#ffaa00' : '#ff4444'
                        }}
                      >
                        {opp.ai_analysis.risk_assessment.toUpperCase()}
                      </span>
                    </div>
                  </div>
                  <div className="ai-reasoning">
                    <div className="ai-reasoning-label">Reasoning:</div>
                    <div className="ai-reasoning-text">{opp.ai_analysis.reasoning}</div>
                  </div>
                </div>
              )}

              <button
                className="trade-single-pair-btn"
                onClick={(e) => {
                  e.stopPropagation();
                  startTradingSinglePair(opp.symbol);
                }}
                disabled={botRunning}
              >
                {botRunning ? 'Trading Active' : 'Trade This Pair'}
              </button>

              {isSelected && (
                <div className="selected-badge">✓ Selected for Trading</div>
              )}
            </div>
          );
          })
        )}
      </div>

      <TradingSettings
        isOpen={showSettings}
        onClose={() => setShowSettings(false)}
        onStart={handleStartTrading}
        selectedPairsCount={selectedPairs.length}
      />
    </div>
  );
}

export default MarketScanner;
