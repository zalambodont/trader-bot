import React, { useState, useEffect } from 'react';
import './AIAnalysisPanel.css';

function AIAnalysisPanel({ analyses = [] }) {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isExpanded, setIsExpanded] = useState(true);

  // Auto-advance disabled - user controls navigation manually
  // useEffect(() => {
  //   if (analyses.length <= 1) return;
  //
  //   const interval = setInterval(() => {
  //     setCurrentIndex((prev) => (prev + 1) % analyses.length);
  //   }, 10000);
  //
  //   return () => clearInterval(interval);
  // }, [analyses.length]);

  // Update to latest when new analysis arrives
  useEffect(() => {
    if (analyses.length > 0) {
      setCurrentIndex(analyses.length - 1);
    }
  }, [analyses.length]);

  const nextAnalysis = () => {
    setCurrentIndex((prev) => (prev + 1) % analyses.length);
  };

  const prevAnalysis = () => {
    setCurrentIndex((prev) => (prev - 1 + analyses.length) % analyses.length);
  };

  if (analyses.length === 0) {
    return (
      <div className="ai-analysis-panel empty">
        <div className="panel-header">
          <h3>🤖 AI Trading Advisor</h3>
        </div>
        <div className="empty-state">
          <p>No AI analysis yet</p>
          <p className="hint">Search for pairs or scan the market to see AI recommendations</p>
        </div>
      </div>
    );
  }

  const currentAnalysis = analyses[currentIndex];
  const { symbol, analysis, timestamp } = currentAnalysis;

  const getTradeDecisionColor = (shouldTrade) => {
    return shouldTrade ? '#00ff00' : '#ff4444';
  };

  const getConfidenceColor = (confidence) => {
    if (confidence >= 0.8) return '#00ff00';
    if (confidence >= 0.6) return '#7fff00';
    if (confidence >= 0.4) return '#ffaa00';
    return '#ff4444';
  };

  const getRiskColor = (risk) => {
    if (risk === 'low') return '#00ff00';
    if (risk === 'medium') return '#ffaa00';
    return '#ff4444';
  };

  return (
    <div className={`ai-analysis-panel ${isExpanded ? 'expanded' : 'collapsed'}`}>
      <div className="panel-header" onClick={() => setIsExpanded(!isExpanded)}>
        <h3>🤖 AI Trading Advisor</h3>
        <div className="header-controls">
          {analyses.length > 1 && (
            <span className="analysis-counter">
              {currentIndex + 1} / {analyses.length}
            </span>
          )}
          <button className="toggle-btn" onClick={(e) => {
            e.stopPropagation();
            setIsExpanded(!isExpanded);
          }}>
            {isExpanded ? '▼' : '▲'}
          </button>
        </div>
      </div>

      {isExpanded && (
        <div className="panel-content">
          <div className="analysis-header">
            <div className="symbol-badge">{symbol}</div>
            <div className="timestamp">{new Date(timestamp).toLocaleTimeString()}</div>
          </div>

          <div className="analysis-metrics">
            <div className="metric">
              <label>Decision</label>
              <div
                className="metric-value decision"
                style={{ color: getTradeDecisionColor(analysis.should_trade) }}
              >
                {analysis.should_trade ? '✅ TRADE' : '❌ SKIP'}
              </div>
            </div>

            <div className="metric">
              <label>Confidence</label>
              <div
                className="metric-value"
                style={{ color: getConfidenceColor(analysis.confidence) }}
              >
                {(analysis.confidence * 100).toFixed(0)}%
              </div>
            </div>

            <div className="metric">
              <label>Risk</label>
              <div
                className="metric-value"
                style={{ color: getRiskColor(analysis.risk_assessment) }}
              >
                {analysis.risk_assessment.toUpperCase()}
              </div>
            </div>
          </div>

          <div className="reasoning-section">
            <label>AI Reasoning</label>
            <div className="reasoning-text">
              {analysis.reasoning}
            </div>
          </div>

          {analyses.length > 1 && (
            <div className="carousel-controls">
              <button onClick={prevAnalysis} className="carousel-btn">
                ◀ Previous
              </button>
              <div className="dots">
                {analyses.map((_, idx) => (
                  <span
                    key={idx}
                    className={`dot ${idx === currentIndex ? 'active' : ''}`}
                    onClick={() => setCurrentIndex(idx)}
                  />
                ))}
              </div>
              <button onClick={nextAnalysis} className="carousel-btn">
                Next ▶
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default AIAnalysisPanel;
