import React, { useState, useEffect } from 'react';
import axios from 'axios';
import TradingSettings from './TradingSettings';
import './PairSearch.css';
import { logAIAnalysis, logWarning } from '../apiLogger';

const API_URL = 'http://localhost:5001';

function PairSearch({ selectedPairs, onPairSelect }) {
  const [searchQuery, setSearchQuery] = useState('');
  const [allPairs, setAllPairs] = useState([]);
  const [showDropdown, setShowDropdown] = useState(false);
  const [searchedPairs, setSearchedPairs] = useState([]);
  const [loading, setLoading] = useState(false);
  const [showSettings, setShowSettings] = useState(false);
  const [botRunning, setBotRunning] = useState(false);
  const [isPairsCollapsed, setIsPairsCollapsed] = useState(false);

  useEffect(() => {
    fetchAllPairs();
    checkBotStatus();
    // Check bot status periodically
    const interval = setInterval(checkBotStatus, 10000);
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

  const fetchAllPairs = async () => {
    try {
      console.log('Fetching ALL Binance pairs from', `${API_URL}/api/pairs`);
      const response = await axios.get(`${API_URL}/api/pairs`);
      console.log('Received', response.data.count, 'pairs from Binance');
      if (response.data.pairs && Array.isArray(response.data.pairs)) {
        setAllPairs(response.data.pairs);
        console.log('✓ Loaded', response.data.pairs.length, 'REAL Binance pairs');
      } else {
        throw new Error('Invalid response from API');
      }
    } catch (error) {
      console.error('✗ FAILED to fetch real Binance pairs:', error.message);
      alert('ERROR: Cannot load Binance pairs. Check API server and try again.');
      setAllPairs([]);
    }
  };

  const handleSearchChange = (e) => {
    setSearchQuery(e.target.value);
    setShowDropdown(e.target.value.length > 0);
  };

  const addPairToSearch = async (pair) => {
    setSearchQuery('');
    setShowDropdown(false);

    // Check if already searched
    if (searchedPairs.find(p => p.symbol === pair)) {
      return;
    }

    setLoading(true);

    try {
      // Fetch pair data from scanner
      const response = await axios.post(`${API_URL}/api/scanner/analyze-pair`, {
        symbol: pair,
        timeframe: '15m'
      });

      if (response.data.success && response.data.opportunity) {
        const opportunity = response.data.opportunity;

        // Log AI analysis if present
        if (opportunity.ai_analysis) {
          console.log(`%c🔍 PAIR SEARCH: ${pair}`, 'color: #00ccff; font-weight: bold; font-size: 14px;');
          logAIAnalysis(opportunity.ai_analysis, `Pair Search Result for ${pair}`);
        } else {
          logWarning(`No AI analysis returned for ${pair}`, opportunity);
        }

        setSearchedPairs(prev => [...prev, opportunity]);
      }
    } catch (error) {
      console.error('Failed to fetch pair data:', error);
      // Add basic info even if analysis fails
      setSearchedPairs(prev => [...prev, {
        symbol: pair,
        price: 0,
        score: 0,
        direction: 'N/A',
        rsi: 0,
        volume_24h: 0,
        volatility: 0,
        signals: []
      }]);
    } finally {
      setLoading(false);
    }
  };

  const removePairFromSearch = (symbol) => {
    setSearchedPairs(prev => prev.filter(p => p.symbol !== symbol));
  };

  const filteredPairs = allPairs.filter(pair =>
    pair.toLowerCase().includes(searchQuery.toLowerCase())
  ).slice(0, 20);

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
        setShowSettings(false);
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

  const selectAllSearched = () => {
    searchedPairs.forEach(pair => {
      if (!selectedPairs.includes(pair.symbol)) {
        onPairSelect(pair.symbol);
      }
    });
  };

  const clearSelection = () => {
    selectedPairs.forEach(pair => onPairSelect(pair));
  };

  const togglePairsAccordion = () => {
    setIsPairsCollapsed(prev => !prev);
  };

  const handlePairsHeaderKeyDown = (event) => {
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault();
      togglePairsAccordion();
    }
  };

  return (
    <div className="pair-search">
      <div
        className={`pair-search-header ${isPairsCollapsed ? 'collapsed' : ''}`}
        onClick={togglePairsAccordion}
        onKeyDown={handlePairsHeaderKeyDown}
        role="button"
        tabIndex={0}
      >
        <div className="pair-search-header-text">
          <h2>🔍 Search & Analyze Pairs</h2>
          <p className="search-subtitle">Search for any trading pair and see its technical analysis</p>
        </div>
        <span className="accordion-toggle-icon" aria-hidden="true">
          {isPairsCollapsed ? 'Expand' : 'Collapse'}
        </span>
      </div>

      {!isPairsCollapsed && (
        <div className="search-controls">
          <div className="search-container">
            <input
              type="text"
              value={searchQuery}
              onChange={handleSearchChange}
              placeholder="Search for pairs (e.g., BTC, ETH, DASH, ZEC)..."
              className="search-input-large"
              onFocus={() => setShowDropdown(searchQuery.length > 0)}
              onBlur={() => setTimeout(() => setShowDropdown(false), 200)}
            />
            {showDropdown && filteredPairs.length > 0 && (
              <div className="search-dropdown-large">
                {filteredPairs.map(pair => (
                  <div
                    key={pair}
                    className="dropdown-item-large"
                    onClick={() => addPairToSearch(pair)}
                  >
                    <span className="pair-name">{pair}</span>
                    <span className="add-icon">+</span>
                  </div>
                ))}
              </div>
            )}
            {showDropdown && filteredPairs.length === 0 && searchQuery.length > 0 && (
              <div className="search-dropdown-large">
                <div className="dropdown-item-large no-results">
                  No pairs found for "{searchQuery}"
                </div>
              </div>
            )}
          </div>
          {loading && <span className="loading-spinner">Analyzing...</span>}
        </div>
      )}

      {searchedPairs.length > 0 && (
        <>
          {!isPairsCollapsed && (
            <div className="selection-controls">
              <div className="selection-info">
                <h3>Analyzed Pairs ({searchedPairs.length})</h3>
                {selectedPairs.length > 0 && (
                  <span className="selected-count">
                    {selectedPairs.length} pair{selectedPairs.length !== 1 ? 's' : ''} selected
                  </span>
                )}
              </div>
              <div className="selection-buttons">
                <button onClick={selectAllSearched} className="select-btn">Select All</button>
                <button onClick={clearSelection} className="select-btn">Clear Selection</button>
                <button
                  onClick={() => setSearchedPairs([])}
                  className="clear-all-btn"
                >
                  Clear All Pairs
                </button>
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

          <div
            className={`searched-pairs-grid ${isPairsCollapsed ? 'collapsed' : ''}`}
            aria-hidden={isPairsCollapsed}
          >
            {searchedPairs.map((pair, index) => {
              const isSelected = selectedPairs.includes(pair.symbol);
              return (
                <div
                  key={index}
                  className={`pair-card ${isSelected ? 'selected' : ''}`}
                  onClick={() => onPairSelect(pair.symbol)}
                >
                  <button
                    className="remove-pair-btn"
                    onClick={(e) => {
                      e.stopPropagation();
                      removePairFromSearch(pair.symbol);
                    }}
                  >
                    ×
                  </button>

                  <div className="pair-card-header">
                    <div className="pair-symbol-wrapper">
                      <input
                        type="checkbox"
                        checked={isSelected}
                        onChange={() => {}}
                        className="pair-checkbox"
                      />
                      <span className="pair-symbol">{pair.symbol}</span>
                    </div>
                    <span
                      className="pair-score"
                      style={{ color: getScoreColor(pair.score) }}
                    >
                      {pair.score}/100
                    </span>
                  </div>

                  <div className="pair-details">
                    <div className="pair-row">
                      <span>Direction:</span>
                      <strong style={{ color: getDirectionColor(pair.direction) }}>
                        {pair.direction || 'NEUTRAL'}
                      </strong>
                    </div>
                    <div className="pair-row">
                      <span>Price:</span>
                      <strong>${pair.price.toFixed(8)}</strong>
                    </div>
                    <div className="pair-row">
                      <span>RSI:</span>
                      <strong style={{
                        color: pair.rsi < 30 ? '#00ff00' :
                               pair.rsi > 70 ? '#ff4444' : '#fff'
                      }}>
                        {pair.rsi.toFixed(1)}
                      </strong>
                    </div>
                    <div className="pair-row">
                      <span>24h Volume:</span>
                      <strong>${pair.volume_24h ? (pair.volume_24h / 1000000).toFixed(2) : '0.00'}M</strong>
                    </div>
                    <div className="pair-row">
                      <span>Volatility:</span>
                      <strong>{pair.volatility.toFixed(2)}%</strong>
                    </div>
                  </div>

                  <div className="pair-signals">
                    {pair.signals && pair.signals.length > 0 ? (
                      pair.signals.map((signal, i) => (
                        <span key={i} className="signal-tag">{signal}</span>
                      ))
                    ) : (
                      <span className="no-signals">No signals</span>
                    )}
                  </div>

                  {isSelected && (
                    <div className="selected-badge">✓ Selected for Trading</div>
                  )}
                </div>
              );
            })}
          </div>
        </>
      )}

      {!isPairsCollapsed && searchedPairs.length === 0 && (
        <div className="empty-search">
          <p>🔎 Search for pairs above to see their technical analysis</p>
          <p className="hint">Try searching: BTC, ETH, DASH, ZEC, SOL, ADA...</p>
        </div>
      )}

      <TradingSettings
        isOpen={showSettings}
        onClose={() => setShowSettings(false)}
        onStart={handleStartTrading}
      />
    </div>
  );
}

export default PairSearch;
