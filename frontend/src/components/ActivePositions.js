import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import { LineChart, Line, Tooltip, ResponsiveContainer } from 'recharts';
import './ActivePositions.css';
import { logAIAnalysis } from '../apiLogger';

const API_URL = 'http://localhost:5001';

function ActivePositions() {
  const [positions, setPositions] = useState([]);
  const [portfolio, setPortfolio] = useState(null);
  const [chartData, setChartData] = useState({});
  const [tradeHistory, setTradeHistory] = useState([]);

  const fetchPositions = useCallback(async () => {
    try {
      const response = await axios.get(`${API_URL}/api/multi-bot/status`);
      if (response.data.portfolio) {
        const positions = response.data.portfolio.positions || [];

        setPositions(positions);
        setPortfolio(response.data.portfolio);

        // Fetch chart data for each position
        positions.forEach(pos => {
          fetchChartForSymbol(pos.symbol);
        });
      }
    } catch (error) {
      console.error('Failed to fetch positions:', error);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const fetchTradeHistory = useCallback(async () => {
    try {
      const response = await axios.get(`${API_URL}/api/multi-bot/trade-history?hours=24`);
      if (response.data.trades) {
        const trades = response.data.trades || [];

        setTradeHistory(trades);
      }
    } catch (error) {
      console.error('Failed to fetch trade history:', error);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    fetchPositions();
    fetchTradeHistory();
    const interval = setInterval(() => {
      fetchPositions();
      fetchTradeHistory();
    }, 10000); // Update every 10 seconds
    return () => clearInterval(interval);
  }, [fetchPositions, fetchTradeHistory]);

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

              {pos.ai_analysis && (
                <div className="position-ai-analysis">
                  <div className="ai-header">🤖 AI Analysis</div>
                  <div className="ai-metrics-compact">
                    <div className="ai-metric-compact">
                      <span className="ai-label">Decision:</span>
                      <span
                        className="ai-value"
                        style={{ color: pos.ai_analysis.should_trade ? '#00ff00' : '#ff4444' }}
                      >
                        {pos.ai_analysis.should_trade ? '✅ TRADE' : '❌ SKIP'}
                      </span>
                    </div>
                    <div className="ai-metric-compact">
                      <span className="ai-label">Confidence:</span>
                      <span
                        className="ai-value"
                        style={{
                          color: pos.ai_analysis.confidence >= 0.7 ? '#00ff00' :
                                 pos.ai_analysis.confidence >= 0.5 ? '#ffaa00' : '#ff4444'
                        }}
                      >
                        {(pos.ai_analysis.confidence * 100).toFixed(0)}%
                      </span>
                    </div>
                    <div className="ai-metric-compact">
                      <span className="ai-label">Risk:</span>
                      <span
                        className="ai-value"
                        style={{
                          color: pos.ai_analysis.risk_assessment === 'low' ? '#00ff00' :
                                 pos.ai_analysis.risk_assessment === 'medium' ? '#ffaa00' : '#ff4444'
                        }}
                      >
                        {pos.ai_analysis.risk_assessment.toUpperCase()}
                      </span>
                    </div>
                  </div>
                </div>
              )}
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

      {tradeHistory.length > 0 && (
        <div className="trade-history-section">
          <h4>24-Hour Trade History ({tradeHistory.length})</h4>
          <div className="table-container">
            <table className="trade-history-table">
              <thead>
                <tr>
                  <th>Symbol</th>
                  <th>Direction</th>
                  <th>Entry Price</th>
                  <th>Exit Price</th>
                  <th>Quantity</th>
                  <th>P&L</th>
                  <th>P&L %</th>
                  <th>Reason</th>
                  <th>Exit Time</th>
                </tr>
              </thead>
              <tbody>
                {tradeHistory.map((trade, index) => (
                  <tr key={index} className={trade.pnl >= 0 ? 'trade-win' : 'trade-loss'}>
                    <td className="trade-symbol">{trade.symbol}</td>
                    <td className="trade-direction" style={{ color: getDirectionColor(trade.direction) }}>
                      {trade.direction}
                    </td>
                    <td>${trade.entry_price?.toFixed(8)}</td>
                    <td>${trade.exit_price?.toFixed(8)}</td>
                    <td>{trade.quantity?.toFixed(6)}</td>
                    <td style={{ color: getPnLColor(trade.pnl), fontWeight: 'bold' }}>
                      {trade.pnl >= 0 ? '+' : ''}${trade.pnl?.toFixed(2)}
                    </td>
                    <td style={{ color: getPnLColor(trade.pnl_pct), fontWeight: 'bold' }}>
                      {trade.pnl_pct >= 0 ? '+' : ''}{trade.pnl_pct?.toFixed(2)}%
                    </td>
                    <td className="trade-reason">{trade.reason}</td>
                    <td className="trade-time">
                      {new Date(trade.exit_time).toLocaleString('en-US', {
                        month: 'short',
                        day: 'numeric',
                        hour: '2-digit',
                        minute: '2-digit'
                      })}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}

export default ActivePositions;
