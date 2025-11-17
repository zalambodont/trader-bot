import React from 'react';
import './ControlPanel.css';

function ControlPanel({ status, onStart, onStop, onBacktest }) {
  return (
    <div className="panel control-panel">
      <h2>Controls</h2>

      <div className="controls">
        {!status.running ? (
          <button className="btn btn-start" onClick={onStart}>
            Start Bot
          </button>
        ) : (
          <button className="btn btn-stop" onClick={onStop}>
            Stop Bot
          </button>
        )}

        <button className="btn btn-backtest" onClick={onBacktest}>
          Run Backtest
        </button>
      </div>

      <div className="warning-box">
        <h3>WARNING</h3>
        <p>
          {status.mode === 'paper' ? (
            <>This is PAPER TRADING mode. No real money is at risk.</>
          ) : (
            <>This is LIVE TRADING mode. Real money is at risk!</>
          )}
        </p>
        <p className="disclaimer">
          Cryptocurrency trading is extremely risky. You can lose all your money.
          Never invest more than you can afford to lose.
        </p>
      </div>
    </div>
  );
}

export default ControlPanel;
