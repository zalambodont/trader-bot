import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './PairSearch.css';

const API_URL = 'http://localhost:5001';

function PairSearch({ selectedPairs, onPairSelect }) {
  const [searchQuery, setSearchQuery] = useState('');
  const [allPairs, setAllPairs] = useState([]);
  const [showDropdown, setShowDropdown] = useState(false);
  const [searchedPairs, setSearchedPairs] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchAllPairs();
  }, []);

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
        setSearchedPairs(prev => [...prev, response.data.opportunity]);
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

  return (
    <div className="pair-search">
      <div className="pair-search-header">
        <h2>🔍 Search & Analyze Pairs</h2>
        <p className="search-subtitle">Search for any trading pair and see its technical analysis</p>
      </div>

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

      {searchedPairs.length > 0 && (
        <>
          <div className="searched-pairs-header">
            <h3>Analyzed Pairs ({searchedPairs.length})</h3>
            <button
              onClick={() => setSearchedPairs([])}
              className="clear-all-btn"
            >
              Clear All
            </button>
          </div>

          <div className="searched-pairs-grid">
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
                      <strong>${(pair.volume_24h / 1000000).toFixed(2)}M</strong>
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

      {searchedPairs.length === 0 && (
        <div className="empty-search">
          <p>🔎 Search for pairs above to see their technical analysis</p>
          <p className="hint">Try searching: BTC, ETH, DASH, ZEC, SOL, ADA...</p>
        </div>
      )}
    </div>
  );
}

export default PairSearch;
