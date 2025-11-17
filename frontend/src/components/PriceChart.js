import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import './PriceChart.css';

function PriceChart({ data, symbol }) {
  if (!data || data.length === 0) {
    return (
      <div className="panel chart-panel">
        <h2>{symbol} Price Chart</h2>
        <div className="chart-loading">Loading chart data...</div>
      </div>
    );
  }

  // Format data for chart
  const chartData = data.map(item => ({
    time: new Date(item.timestamp).toLocaleTimeString(),
    price: parseFloat(item.close),
    sma_20: item.sma_20 ? parseFloat(item.sma_20) : null,
    sma_50: item.sma_50 ? parseFloat(item.sma_50) : null,
  }));

  return (
    <div className="panel chart-panel">
      <h2>{symbol} Price Chart (15m)</h2>
      <ResponsiveContainer width="100%" height={400}>
        <LineChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
          <XAxis
            dataKey="time"
            stroke="rgba(255,255,255,0.6)"
            tick={{ fontSize: 12 }}
          />
          <YAxis
            stroke="rgba(255,255,255,0.6)"
            tick={{ fontSize: 12 }}
            domain={['auto', 'auto']}
          />
          <Tooltip
            contentStyle={{
              background: 'rgba(10, 14, 39, 0.9)',
              border: '1px solid rgba(255,255,255,0.2)',
              borderRadius: '8px',
              color: '#fff'
            }}
          />
          <Legend />
          <Line
            type="monotone"
            dataKey="price"
            stroke="#10b981"
            strokeWidth={2}
            dot={false}
            name="Price"
          />
          <Line
            type="monotone"
            dataKey="sma_20"
            stroke="#3b82f6"
            strokeWidth={1.5}
            dot={false}
            name="SMA 20"
          />
          <Line
            type="monotone"
            dataKey="sma_50"
            stroke="#f59e0b"
            strokeWidth={1.5}
            dot={false}
            name="SMA 50"
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}

export default PriceChart;
