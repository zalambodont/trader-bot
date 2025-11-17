import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import { LineChart, Line, Tooltip, ResponsiveContainer } from 'recharts';
import './ActivePositions.css';

const API_URL = 'http://localhost:5001';

function ActivePositions() {
  const [positions, setPositions] = useState([]);
  const [portfolio, setPortfolio] = useState(null);
  const [chartData, setChartData] = useState({});

  const fetchPositions = useCallback(async () => {
    try {
      const response = await axios.get(`${API_URL}/api/multi-bot/status`);
      if (response.data.portfolio) {
        setPositions(response.data.portfolio.positions || []);
        setPortfolio(response.data.portfolio);

        // Fetch chart data for each position
        response.data.portfolio.positions?.forEach(pos => {
          fetchChartForSymbol(pos.symbol);
        });
      }
    } catch (error) {
      console.error('Failed to fetch positions:', error);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    fetchPositions();
    const interval = setInterval(fetchPositions, 5000); // Update every 5 seconds
    return () => clearInterval(interval);
  }, [fetchPositions]);

  const fetchChartForSymbol = async (symbol) => {
    if (chartData[symbol]) return; // Already have it

    try {
      const response = await axios.get(`${API_URL}/api/chart?symbol=${symbol}&limit=20&interval=15m`);
      if (response.data.data) {
        const formattedData = response.data.data.map((d, i) => ({
          index: i,
          price: d.close
        }));
        setChartData(prev => ({
          ...prev,
          [symbol]: formattedData
        }));
      }
    } catch (error) {
      console.error(`Failed to fetch chart for ${symbol}:`, error);
    }
  };

  const getPnLColor = (pnl) => {
    if (pnl > 0) return '#00ff00';
    if (pnl < 0) return '#ff4444';
    return '#888';
  };

  const getDirectionColor = (direction) => {
    return direction === 'LONG' ? '#00ff00' : '#ff9900';
  };

  if (!portfolio) {
    return (
      <div className="active-positions">
        <h3>Active Positions</h3>
        <p className="no-data">No active trading session</p>
      </div>
    );
  }

  return (
    <div className="active-positions">
      <div className="positions-header">
        <h3>Active Positions ({positions.length}/{portfolio.max_positions})</h3>
        <div className="portfolio-summary">
          <div className="summary-item">
            <span>Total Value:</span>
            <strong>${portfolio.total_value?.toFixed(2) || '0.00'}</strong>
          </div>
          <div className="summary-item">
            <span>P&L:</span>
            <strong style={{ color: getPnLColor(portfolio.total_unrealized_pnl) }}>
              ${portfolio.total_unrealized_pnl?.toFixed(2) || '0.00'}
              ({portfolio.total_return?.toFixed(2) || '0.00'}%)
            </strong>
          </div>
          <div className="summary-item">
            <span>Available:</span>
            <strong>${portfolio.available_capital?.toFixed(2) || '0.00'}</strong>
          </div>
        </div>
      </div>

      {positions.length === 0 ? (
        <div className="no-positions">
          <p>No open positions yet. Waiting for trading signals...</p>
        </div>
      ) : (
        <div className="positions-grid">
          {positions.map((pos, index) => (
            <div key={index} className="position-card">
              <div className="position-header">
                <div>
                  <span className="position-symbol">{pos.symbol}</span>
                  <span
                    className="position-direction"
                    style={{ color: getDirectionColor(pos.direction) }}
                  >
                    {pos.direction}
                  </span>
                </div>
                <span
                  className="position-pnl"
                  style={{ color: getPnLColor(pos.unrealized_pnl) }}
                >
                  {pos.unrealized_pnl > 0 ? '+' : ''}${pos.unrealized_pnl?.toFixed(2) || '0.00'}
                </span>
              </div>

              <div className="position-chart">
                {chartData[pos.symbol] ? (
                  <ResponsiveContainer width="100%" height={80}>
                    <LineChart data={chartData[pos.symbol]}>
                      <Line
                        type="monotone"
                        dataKey="price"
                        stroke={pos.unrealized_pnl > 0 ? '#00ff00' : '#ff4444'}
                        strokeWidth={2}
                        dot={false}
                      />
                      <Tooltip
                        contentStyle={{ background: '#16213e', border: '1px solid #667eea' }}
                        labelStyle={{ color: '#fff' }}
                      />
                    </LineChart>
                  </ResponsiveContainer>
                ) : (
                  <div className="chart-loading">Loading chart...</div>
                )}
              </div>

              <div className="position-details">
                <div className="detail-row">
                  <span>Entry:</span>
                  <strong>${pos.entry_price?.toFixed(8) || '0'}</strong>
                </div>
                <div className="detail-row">
                  <span>Current:</span>
                  <strong>${pos.current_price?.toFixed(8) || '0'}</strong>
                </div>
                <div className="detail-row">
                  <span>Size:</span>
                  <strong>{pos.quantity?.toFixed(6) || '0'}</strong>
                </div>
                <div className="detail-row">
                  <span>Value:</span>
                  <strong>${pos.position_value?.toFixed(2) || '0'}</strong>
                </div>
                <div className="detail-row">
                  <span>Stop Loss:</span>
                  <strong className="stop-loss">${pos.stop_loss?.toFixed(8) || 'N/A'}</strong>
                </div>
                <div className="detail-row">
                  <span>Take Profit:</span>
                  <strong className="take-profit">${pos.take_profit?.toFixed(8) || 'N/A'}</strong>
                </div>
              </div>

              <div className="position-footer">
                <span
                  className="pnl-percentage"
                  style={{ color: getPnLColor(pos.unrealized_pnl_pct) }}
                >
                  {pos.unrealized_pnl_pct > 0 ? '+' : ''}{pos.unrealized_pnl_pct?.toFixed(2) || '0.00'}%
                </span>
              </div>
            </div>
          ))}
        </div>
      )}

      {portfolio.total_trades > 0 && (
        <div className="trading-stats">
          <h4>Session Stats</h4>
          <div className="stats-grid">
            <div className="stat-item">
              <span>Total Trades:</span>
              <strong>{portfolio.total_trades}</strong>
            </div>
            <div className="stat-item">
              <span>Win Rate:</span>
              <strong>{portfolio.win_rate?.toFixed(1) || '0'}%</strong>
            </div>
            <div className="stat-item">
              <span>Avg Win:</span>
              <strong style={{ color: '#00ff00' }}>${portfolio.avg_win?.toFixed(2) || '0.00'}</strong>
            </div>
            <div className="stat-item">
              <span>Avg Loss:</span>
              <strong style={{ color: '#ff4444' }}>${portfolio.avg_loss?.toFixed(2) || '0.00'}</strong>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default ActivePositions;
