import React from 'react';
import './PositionsTable.css';

function PositionsTable({ positions, currentPrice }) {
  const formatCurrency = (value) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(value);
  };

  const calculatePnL = (position) => {
    if (!currentPrice || !position.entry_price) return { pnl: 0, pnlPercent: 0 };

    const pnl = (currentPrice - position.entry_price) * position.quantity;
    const pnlPercent = ((currentPrice - position.entry_price) / position.entry_price) * 100;

    return { pnl, pnlPercent };
  };

  return (
    <div className="panel positions-panel">
      <h2>Open Positions ({positions.length})</h2>

      {positions.length === 0 ? (
        <div className="empty-state">No open positions</div>
      ) : (
        <div className="table-container">
          <table className="positions-table">
            <thead>
              <tr>
                <th>Symbol</th>
                <th>Quantity</th>
                <th>Entry Price</th>
                <th>Current Price</th>
                <th>PnL</th>
              </tr>
            </thead>
            <tbody>
              {positions.map((position, index) => {
                const { pnl, pnlPercent } = calculatePnL(position);
                return (
                  <tr key={index}>
                    <td>{position.symbol}</td>
                    <td>{position.quantity.toFixed(6)}</td>
                    <td>{formatCurrency(position.entry_price)}</td>
                    <td>{formatCurrency(currentPrice)}</td>
                    <td className={pnl >= 0 ? 'positive' : 'negative'}>
                      {formatCurrency(pnl)}
                      <span className="pnl-percent">({pnlPercent >= 0 ? '+' : ''}{pnlPercent.toFixed(2)}%)</span>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

export default PositionsTable;
