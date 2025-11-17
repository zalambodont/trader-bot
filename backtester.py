"""
Backtesting engine to test strategies on historical data
"""
import pandas as pd
import numpy as np
from typing import Dict, List
from datetime import datetime
from strategies import TradingStrategy
from risk_management import RiskManager
from indicators import TechnicalIndicators


class Backtester:
    """Backtest trading strategies on historical data"""

    def __init__(
        self,
        strategy: TradingStrategy,
        initial_balance: float = 10000,
        commission: float = 0.001  # 0.1% trading fee
    ):
        """
        Initialize backtester

        Args:
            strategy: Trading strategy to test
            initial_balance: Starting capital
            commission: Trading commission (0.001 = 0.1%)
        """
        self.strategy = strategy
        self.initial_balance = initial_balance
        self.commission = commission
        self.risk_manager = RiskManager()

        # Trading state
        self.balance = initial_balance
        self.positions = []
        self.trades = []
        self.equity_curve = []

    def run(self, df: pd.DataFrame, verbose: bool = True) -> Dict:
        """
        Run backtest on historical data

        Args:
            df: DataFrame with OHLCV data and indicators
            verbose: Print trade details

        Returns:
            Dictionary with backtest results
        """
        # Add indicators if not present
        df = TechnicalIndicators.add_all_indicators(df)

        if verbose:
            print(f"\n{'='*60}")
            print(f"BACKTESTING: {self.strategy.name}")
            print(f"Period: {df.index[0]} to {df.index[-1]}")
            print(f"Initial Balance: ${self.initial_balance:,.2f}")
            print(f"{'='*60}\n")

        # Iterate through each candle
        for i in range(len(df)):
            current_data = df.iloc[:i+1]

            if len(current_data) < 200:  # Need enough data for indicators
                continue

            timestamp = df.index[i]
            current_price = df.iloc[i]['close']

            # Check existing positions for exit
            self._check_exits(current_price, timestamp, verbose)

            # Get strategy signal
            try:
                action, confidence = self.strategy.analyze(current_data)
            except Exception as e:
                if verbose:
                    print(f"Strategy error at {timestamp}: {e}")
                continue

            # Execute trades based on signal
            if action == 'BUY' and confidence > 0.5:
                if self.risk_manager.can_open_position(self.positions):
                    self._open_position(current_price, timestamp, confidence, verbose)

            elif action == 'SELL' and len(self.positions) > 0:
                self._close_all_positions(current_price, timestamp, "Strategy Signal", verbose)

            # Track equity
            equity = self._calculate_equity(current_price)
            self.equity_curve.append({
                'timestamp': timestamp,
                'equity': equity,
                'balance': self.balance,
                'positions_value': equity - self.balance
            })

        # Close any remaining positions at final price
        if self.positions:
            final_price = df.iloc[-1]['close']
            self._close_all_positions(final_price, df.index[-1], "End of backtest", verbose)

        # Calculate results
        results = self._calculate_results(df, verbose)

        return results

    def _open_position(self, price: float, timestamp, confidence: float, verbose: bool):
        """Open a new position"""
        # Calculate position size
        position_size = self.risk_manager.calculate_position_size(
            self.balance,
            price
        )

        position_value = position_size * price
        commission_cost = position_value * self.commission

        # Check if we have enough balance
        if self.balance < position_value + commission_cost:
            return

        # Open position
        position = {
            'entry_price': price,
            'entry_time': timestamp,
            'size': position_size,
            'value': position_value,
            'confidence': confidence,
            'stop_loss': self.risk_manager.calculate_stop_loss(price, 'BUY'),
            'take_profit': self.risk_manager.calculate_take_profit(price, 'BUY')
        }

        self.positions.append(position)
        self.balance -= (position_value + commission_cost)

        if verbose:
            print(f"[{timestamp}] BUY: {position_size:.6f} @ ${price:.2f} | "
                  f"Confidence: {confidence:.2%} | Balance: ${self.balance:.2f}")

    def _close_position(self, position: Dict, price: float, timestamp, reason: str, verbose: bool):
        """Close a position"""
        exit_value = position['size'] * price
        commission_cost = exit_value * self.commission

        pnl = exit_value - position['value'] - commission_cost
        pnl_percent = (pnl / position['value']) * 100

        # Add to balance
        self.balance += exit_value - commission_cost

        # Record trade
        trade = {
            **position,
            'exit_price': price,
            'exit_time': timestamp,
            'pnl': pnl,
            'pnl_percent': pnl_percent,
            'reason': reason,
            'hold_time': (timestamp - position['entry_time']).total_seconds() / 3600  # hours
        }
        self.trades.append(trade)

        if verbose:
            print(f"[{timestamp}] SELL: {position['size']:.6f} @ ${price:.2f} | "
                  f"PnL: ${pnl:+.2f} ({pnl_percent:+.2f}%) | {reason} | Balance: ${self.balance:.2f}")

    def _close_all_positions(self, price: float, timestamp, reason: str, verbose: bool):
        """Close all open positions"""
        for position in self.positions[:]:
            self._close_position(position, price, timestamp, reason, verbose)
            self.positions.remove(position)

    def _check_exits(self, price: float, timestamp, verbose: bool):
        """Check if any positions should be exited"""
        for position in self.positions[:]:
            should_exit, reason = self.risk_manager.should_exit_position(
                position,
                price
            )

            if should_exit:
                self._close_position(position, price, timestamp, reason, verbose)
                self.positions.remove(position)

    def _calculate_equity(self, current_price: float) -> float:
        """Calculate current total equity"""
        positions_value = sum(p['size'] * current_price for p in self.positions)
        return self.balance + positions_value

    def _calculate_results(self, df: pd.DataFrame, verbose: bool) -> Dict:
        """Calculate backtest performance metrics"""
        final_equity = self._calculate_equity(df.iloc[-1]['close'])
        total_return = ((final_equity - self.initial_balance) / self.initial_balance) * 100

        winning_trades = [t for t in self.trades if t['pnl'] > 0]
        losing_trades = [t for t in self.trades if t['pnl'] < 0]

        win_rate = len(winning_trades) / len(self.trades) * 100 if self.trades else 0

        avg_win = np.mean([t['pnl'] for t in winning_trades]) if winning_trades else 0
        avg_loss = np.mean([t['pnl'] for t in losing_trades]) if losing_trades else 0

        # Calculate max drawdown
        equity_df = pd.DataFrame(self.equity_curve)
        if not equity_df.empty:
            equity_df['peak'] = equity_df['equity'].cummax()
            equity_df['drawdown'] = (equity_df['equity'] - equity_df['peak']) / equity_df['peak']
            max_drawdown = equity_df['drawdown'].min() * 100
        else:
            max_drawdown = 0

        # Sharpe ratio (simplified - assuming 0% risk-free rate)
        if not equity_df.empty and len(equity_df) > 1:
            returns = equity_df['equity'].pct_change().dropna()
            sharpe_ratio = returns.mean() / returns.std() * np.sqrt(252) if returns.std() > 0 else 0
        else:
            sharpe_ratio = 0

        results = {
            'initial_balance': self.initial_balance,
            'final_equity': final_equity,
            'total_return': total_return,
            'total_trades': len(self.trades),
            'winning_trades': len(winning_trades),
            'losing_trades': len(losing_trades),
            'win_rate': win_rate,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'max_drawdown': max_drawdown,
            'sharpe_ratio': sharpe_ratio,
            'profit_factor': abs(sum(t['pnl'] for t in winning_trades) / sum(t['pnl'] for t in losing_trades)) if losing_trades else 0,
            'trades': self.trades,
            'equity_curve': equity_df.to_dict('records') if not equity_df.empty else []
        }

        if verbose:
            print(f"\n{'='*60}")
            print(f"BACKTEST RESULTS")
            print(f"{'='*60}")
            print(f"Initial Balance:    ${results['initial_balance']:,.2f}")
            print(f"Final Equity:       ${results['final_equity']:,.2f}")
            print(f"Total Return:       {results['total_return']:+.2f}%")
            print(f"Max Drawdown:       {results['max_drawdown']:.2f}%")
            print(f"Sharpe Ratio:       {results['sharpe_ratio']:.2f}")
            print(f"\nTrade Statistics:")
            print(f"Total Trades:       {results['total_trades']}")
            print(f"Winning Trades:     {results['winning_trades']}")
            print(f"Losing Trades:      {results['losing_trades']}")
            print(f"Win Rate:           {results['win_rate']:.2f}%")
            print(f"Avg Win:            ${results['avg_win']:.2f}")
            print(f"Avg Loss:           ${results['avg_loss']:.2f}")
            print(f"Profit Factor:      {results['profit_factor']:.2f}")
            print(f"{'='*60}\n")

        return results
