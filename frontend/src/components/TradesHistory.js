import React from 'react';
import './TradesHistory.css';

function TradesHistory({ trades }) {
  const formatCurrency = (value) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(value);
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString();
  };

  // Show only last 10 trades
  const recentTrades = (trades || []).slice(-10).reverse();

  return (
    <div className="panel trades-panel">
      <h2>Recent Trades ({trades ? trades.length : 0})</h2>

      {recentTrades.length === 0 ? (
        <div className="empty-state">No trades yet</div>
      ) : (
        <div className="table-container">
          <table className="trades-table">
            <thead>
              <tr>
                <th>Time</th>
                <th>Entry</th>
                <th>Exit</th>
                <th>PnL</th>
              </tr>
            </thead>
            <tbody>
              {recentTrades.map((trade, index) => (
                <tr key={index}>
                  <td className="trade-time">
                    {trade.exit_time ? formatDate(trade.exit_time) : 'Open'}
                  </td>
                  <td>{formatCurrency(trade.entry_price || 0)}</td>
                  <td>{trade.exit_price ? formatCurrency(trade.exit_price) : '-'}</td>
                  <td className={trade.pnl >= 0 ? 'positive' : 'negative'}>
                    {trade.pnl ? formatCurrency(trade.pnl) : '-'}
                    {trade.pnl_percent && (
                      <span className="pnl-percent">
                        ({trade.pnl_percent >= 0 ? '+' : ''}{trade.pnl_percent.toFixed(2)}%)
                      </span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

export default TradesHistory;
