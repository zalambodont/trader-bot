import React from 'react';
import './StatsPanel.css';

function StatsPanel({ status }) {
  const formatCurrency = (value) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(value);
  };

  const formatPercent = (value) => {
    const sign = value >= 0 ? '+' : '';
    return `${sign}${value.toFixed(2)}%`;
  };

  return (
    <div className="panel stats-panel">
      <h2>Statistics</h2>

      <div className="stat-group">
        <div className="stat-item">
          <span className="stat-label">Current Price</span>
          <span className="stat-value price">{formatCurrency(status.current_price)}</span>
        </div>

        <div className="stat-item">
          <span className="stat-label">Portfolio Value</span>
          <span className="stat-value">{formatCurrency(status.portfolio_value)}</span>
        </div>

        <div className="stat-item">
          <span className="stat-label">Available Balance</span>
          <span className="stat-value">{formatCurrency(status.balance)}</span>
        </div>

        <div className="stat-item">
          <span className="stat-label">Total Return</span>
          <span className={`stat-value ${status.total_return >= 0 ? 'positive' : 'negative'}`}>
            {formatPercent(status.total_return)}
          </span>
        </div>
      </div>

      <div className="divider"></div>

      <div className="stat-group">
        <div className="stat-item">
          <span className="stat-label">Strategy</span>
          <span className="stat-value small">{status.strategy.toUpperCase()}</span>
        </div>

        <div className="stat-item">
          <span className="stat-label">Symbol</span>
          <span className="stat-value small">{status.symbol}</span>
        </div>

        <div className="stat-item">
          <span className="stat-label">Open Positions</span>
          <span className="stat-value small">{status.open_positions} / {status.max_positions}</span>
        </div>

        <div className="stat-item">
          <span className="stat-label">Last Signal</span>
          <span className={`stat-value small signal-${status.last_signal.action.toLowerCase()}`}>
            {status.last_signal.action} ({(status.last_signal.confidence * 100).toFixed(0)}%)
          </span>
        </div>
      </div>

      {status.performance && status.performance.total_trades > 0 && (
        <>
          <div className="divider"></div>
          <div className="stat-group">
            <div className="stat-item">
              <span className="stat-label">Total Trades</span>
              <span className="stat-value small">{status.performance.total_trades}</span>
            </div>

            <div className="stat-item">
              <span className="stat-label">Win Rate</span>
              <span className="stat-value small">{status.performance.win_rate.toFixed(1)}%</span>
            </div>

            <div className="stat-item">
              <span className="stat-label">Total PnL</span>
              <span className={`stat-value small ${status.performance.total_pnl >= 0 ? 'positive' : 'negative'}`}>
                {formatCurrency(status.performance.total_pnl || 0)}
              </span>
            </div>
          </div>
        </>
      )}
    </div>
  );
}

export default StatsPanel;
