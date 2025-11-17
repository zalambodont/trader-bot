import React, { useState } from 'react';
import './TradingSettings.css';

function TradingSettings({ isOpen, onClose, onStart, initialSettings }) {
  const [settings, setSettings] = useState({
    totalCapital: initialSettings?.totalCapital || 10000,
    maxPositions: initialSettings?.maxPositions || 5,
    stopLossPct: initialSettings?.stopLossPct || 2,
    takeProfitPct: initialSettings?.takeProfitPct || 4,
    scanInterval: initialSettings?.scanInterval || 60,
    minScore: initialSettings?.minScore || 60,
    tradingMode: initialSettings?.tradingMode || 'paper'
  });

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
              <label>Total Capital (USDT)</label>
              <input
                type="number"
                value={settings.totalCapital}
                onChange={(e) => handleChange('totalCapital', parseFloat(e.target.value) || 0)}
                min="100"
                step="100"
                required
              />
              <span className="help-text">Total amount to allocate across all positions</span>
            </div>

            <div className="form-group">
              <label>Max Simultaneous Positions</label>
              <input
                type="number"
                value={settings.maxPositions}
                onChange={(e) => handleChange('maxPositions', parseInt(e.target.value) || 1)}
                min="1"
                max="20"
                required
              />
              <span className="help-text">
                Capital per position: ${(settings.totalCapital / settings.maxPositions).toFixed(2)}
              </span>
            </div>
          </div>

          <div className="settings-section">
            <h3>Risk Management</h3>

            <div className="form-group">
              <label>Stop Loss (%)</label>
              <input
                type="number"
                value={settings.stopLossPct}
                onChange={(e) => handleChange('stopLossPct', parseFloat(e.target.value) || 0)}
                min="0.5"
                max="10"
                step="0.5"
                required
              />
              <span className="help-text">Exit position if price drops by this %</span>
            </div>

            <div className="form-group">
              <label>Take Profit (%)</label>
              <input
                type="number"
                value={settings.takeProfitPct}
                onChange={(e) => handleChange('takeProfitPct', parseFloat(e.target.value) || 0)}
                min="0.5"
                max="20"
                step="0.5"
                required
              />
              <span className="help-text">Exit position if price rises by this %</span>
            </div>
          </div>

          <div className="settings-section">
            <h3>Scanning Settings</h3>

            <div className="form-group">
              <label>Scan Interval (seconds)</label>
              <input
                type="number"
                value={settings.scanInterval}
                onChange={(e) => handleChange('scanInterval', parseInt(e.target.value) || 30)}
                min="30"
                max="600"
                step="30"
                required
              />
              <span className="help-text">How often to check for new opportunities</span>
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
