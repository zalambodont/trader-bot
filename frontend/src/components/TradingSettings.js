import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './TradingSettings.css';

const API_URL = 'http://localhost:5001';

function TradingSettings({ isOpen, onClose, onStart, initialSettings, pairData }) {
  const [settings, setSettings] = useState({
    totalCapital: initialSettings?.totalCapital || 10000,
    maxPositions: 999, // Unlimited positions - each trade is independent
    stopLossPct: initialSettings?.stopLossPct || 2,
    takeProfitPct: initialSettings?.takeProfitPct || 4,
    scanInterval: initialSettings?.scanInterval || 60,
    minScore: initialSettings?.minScore || 60,
    tradingMode: initialSettings?.tradingMode || 'paper',
    leverage: initialSettings?.leverage || 1,
    direction: initialSettings?.direction || 'LONG'
  });

  const [aiSuggestion, setAiSuggestion] = useState(null);
  const [loadingAiSuggestion, setLoadingAiSuggestion] = useState(false);
  const [unsafeMode, setUnsafeMode] = useState(false);

  // Fetch AI direction suggestion when modal opens with pair data
  useEffect(() => {
    if (isOpen && pairData) {
      fetchAiDirectionSuggestion();
    }
  }, [isOpen, pairData]);

  const fetchAiDirectionSuggestion = async () => {
    if (!pairData?.symbol) return;

    setLoadingAiSuggestion(true);
    try {
      const response = await axios.post(`${API_URL}/api/ai/suggest-direction`, {
        symbol: pairData.symbol,
        opportunity: pairData
      });

      if (response.data.success) {
        setAiSuggestion(response.data.suggestion);
        // Auto-select AI suggested direction
        if (response.data.suggestion?.direction) {
          setSettings(prev => ({
            ...prev,
            direction: response.data.suggestion.direction
          }));
        }
      }
    } catch (error) {
      console.error('Failed to get AI direction suggestion:', error);
    } finally {
      setLoadingAiSuggestion(false);
    }
  };

  const handleChange = (field, value) => {
    // Prevent NaN values
    if (typeof value === 'number' && isNaN(value)) {
      return;
    }
    setSettings(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    // maxPositions is already synced with selectedPairsCount via useEffect
    onStart(settings);
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>Trading Settings</h2>
          <button className="close-btn" onClick={onClose}>&times;</button>
        </div>

        <form onSubmit={handleSubmit} className="settings-form">
          <div className="settings-section">
            <h3>Capital Management</h3>

            <div className="form-group">
              <label>Capital to Trade (USDT)</label>
              <input
                type="number"
                value={settings.totalCapital}
                onChange={(e) => handleChange('totalCapital', parseFloat(e.target.value) || 0)}
                min="100"
                step="100"
                required
              />
              <span className="help-text">Amount to use for this trade</span>
            </div>
          </div>

          <div className="settings-section">
            <h3>Position Settings</h3>

            <div className="form-group">
              <label>Position Direction</label>
              <div className="direction-selector">
                <button
                  type="button"
                  className={`direction-btn long ${settings.direction === 'LONG' ? 'active' : ''}`}
                  onClick={() => handleChange('direction', 'LONG')}
                >
                  LONG
                </button>
                <button
                  type="button"
                  className={`direction-btn short ${settings.direction === 'SHORT' ? 'active' : ''}`}
                  onClick={() => handleChange('direction', 'SHORT')}
                >
                  SHORT
                </button>
              </div>
              {loadingAiSuggestion && (
                <div className="ai-suggestion-loading">
                  <span className="loading-spinner-small"></span> AI analyzing direction...
                </div>
              )}
              {aiSuggestion && !loadingAiSuggestion && (
                <div className={`ai-suggestion-box ${aiSuggestion.direction === 'LONG' ? 'long' : 'short'}`}>
                  <div className="ai-suggestion-header">
                    <span className="ai-icon">🤖</span> AI Suggestion: <strong>{aiSuggestion.direction}</strong>
                    <span className="ai-confidence">({(aiSuggestion.confidence * 100).toFixed(0)}% confident)</span>
                  </div>
                  <div className="ai-suggestion-reasoning">{aiSuggestion.reasoning}</div>
                </div>
              )}
              <span className="help-text">LONG = profit when price goes up, SHORT = profit when price goes down</span>
            </div>

            <div className="form-group">
              <label>Leverage: {settings.leverage}x</label>
              <input
                type="range"
                min="1"
                max="20"
                step="1"
                value={settings.leverage}
                onChange={(e) => handleChange('leverage', parseInt(e.target.value))}
                className="leverage-slider"
              />
              <div className="leverage-labels">
                <span>1x</span>
                <span>5x</span>
                <span>10x</span>
                <span>15x</span>
                <span>20x</span>
              </div>
              {settings.leverage > 5 && (
                <div className="warning-box">
                  ⚠️ High leverage ({settings.leverage}x) significantly increases risk!
                </div>
              )}
              <span className="help-text">Higher leverage = higher risk & reward. Effective capital: ${(settings.totalCapital * settings.leverage).toLocaleString()}</span>
            </div>
          </div>

          <div className="settings-section">
            <h3>Risk Management</h3>

            <div className="form-group">
              <label className="toggle-label">
                <span>Unsafe Mode</span>
                <div className={`toggle-switch ${unsafeMode ? 'active' : ''}`} onClick={() => setUnsafeMode(!unsafeMode)}>
                  <div className="toggle-slider"></div>
                </div>
              </label>
              {unsafeMode && (
                <div className="warning-box danger">
                  ⚠️ UNSAFE MODE: No limits on stop loss/take profit. You can lose 100% of your position!
                </div>
              )}
              <span className="help-text">Enable to remove stop loss and take profit limits</span>
            </div>

            <div className="form-group">
              <label>Minimum Opportunity Score</label>
              <input
                type="number"
                value={settings.minScore}
                onChange={(e) => handleChange('minScore', parseInt(e.target.value) || 1)}
                min="1"
                max="100"
                required
              />
              <span className="help-text">Only trade opportunities above this score</span>
            </div>
            <div className="form-group">
              <label>Stop Loss (%)</label>
              <input
                type="number"
                value={settings.stopLossPct}
                onChange={(e) => handleChange('stopLossPct', parseFloat(e.target.value) || 0)}
                min="0.1"
                max={unsafeMode ? 100 : 10}
                step="0.5"
                required
              />
              <span className="help-text">Exit position if price drops by this % {unsafeMode ? '(unlimited)' : '(max 10%)'}</span>
            </div>

            <div className="form-group">
              <label>Take Profit (%)</label>
              <input
                type="number"
                value={settings.takeProfitPct}
                onChange={(e) => handleChange('takeProfitPct', parseFloat(e.target.value) || 0)}
                min="0.1"
                max={unsafeMode ? 1000 : 20}
                step="0.5"
                required
              />
              <span className="help-text">Exit position if price rises by this % {unsafeMode ? '(unlimited)' : '(max 20%)'}</span>
            </div>
          </div>

          <div className="settings-section">
            <h3>Trading Mode</h3>

            <div className="form-group">
              <div className="radio-group">
                <label className="radio-label">
                  <input
                    type="radio"
                    name="mode"
                    value="paper"
                    checked={settings.tradingMode === 'paper'}
                    onChange={(e) => handleChange('tradingMode', e.target.value)}
                  />
                  <span>Paper Trading (Simulated)</span>
                </label>
                <label className="radio-label">
                  <input
                    type="radio"
                    name="mode"
                    value="live"
                    checked={settings.tradingMode === 'live'}
                    onChange={(e) => handleChange('tradingMode', e.target.value)}
                  />
                  <span>Live Trading (Real Money)</span>
                </label>
              </div>
              {settings.tradingMode === 'live' && (
                <div className="warning-box">
                  ⚠️ Live trading uses real money! Make sure you understand the risks.
                </div>
              )}
            </div>
          </div>

          <div className="form-actions">
            <button type="button" onClick={onClose} className="btn-cancel">
              Cancel
            </button>
            <button type="submit" className="btn-submit">
              Start Trading
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default TradingSettings;
