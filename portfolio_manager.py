"""
Portfolio Manager - Manages multiple simultaneous positions across different pairs
"""
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PortfolioManager:
    """Manages multiple trading positions across different pairs"""

    def __init__(self, initial_balance=10000, max_positions=5, max_allocation_per_trade=0.20):
        """
        Initialize portfolio manager

        Args:
            initial_balance: Starting balance in quote currency (USDT)
            max_positions: Maximum number of simultaneous positions
            max_allocation_per_trade: Max % of portfolio per trade (0.20 = 20%)
        """
        self.initial_balance = initial_balance
        self.balance = initial_balance
        self.max_positions = max_positions
        self.max_allocation_per_trade = max_allocation_per_trade

        self.positions = {}  # {symbol: position_info}
        self.trade_history = []
        self.reserved_capital = 0  # Capital locked in open positions

    def get_available_capital(self):
        """Get capital available for new trades"""
        return self.balance - self.reserved_capital

    def can_open_position(self, symbol):
        """Check if we can open a new position"""
        if symbol in self.positions:
            logger.warning(f"Position already open for {symbol}")
            return False

        if len(self.positions) >= self.max_positions:
            logger.warning(f"Max positions reached ({self.max_positions})")
            return False

        if self.get_available_capital() < self.balance * 0.1:
            logger.warning("Insufficient available capital")
            return False

        return True

    def calculate_position_size(self, symbol, price, direction, risk_amount=None):
        """
        Calculate position size for a trade

        Args:
            symbol: Trading pair
            price: Entry price
            direction: 'LONG' or 'SHORT'
            risk_amount: Amount to risk (if None, uses max_allocation)

        Returns:
            dict with quantity and value
        """
        available = self.get_available_capital()

        if risk_amount is None:
            # Use max allocation percentage
            capital_to_use = self.balance * self.max_allocation_per_trade
        else:
            capital_to_use = min(risk_amount, available)

        # Don't use more than available
        capital_to_use = min(capital_to_use, available)

        # Calculate quantity
        quantity = capital_to_use / price

        return {
            'quantity': quantity,
            'value': capital_to_use,
            'price': price
        }

    def open_position(self, symbol, direction, entry_price, quantity, stop_loss=None, take_profit=None):
        """
        Open a new position

        Args:
            symbol: Trading pair
            direction: 'LONG' or 'SHORT'
            entry_price: Entry price
            quantity: Position size
            stop_loss: Stop loss price (optional)
            take_profit: Take profit price (optional)

        Returns:
            Position info or None if failed
        """
        if not self.can_open_position(symbol):
            return None

        position_value = entry_price * quantity

        position = {
            'symbol': symbol,
            'direction': direction,
            'entry_price': entry_price,
            'current_price': entry_price,
            'quantity': quantity,
            'position_value': position_value,
            'stop_loss': stop_loss,
            'take_profit': take_profit,
            'unrealized_pnl': 0,
            'unrealized_pnl_pct': 0,
            'entry_time': datetime.now().isoformat(),
            'status': 'OPEN'
        }

        self.positions[symbol] = position
        self.reserved_capital += position_value

        logger.info(f"Opened {direction} position for {symbol} at ${entry_price:.8f}, "
                   f"qty: {quantity:.8f}, value: ${position_value:.2f}")

        return position

    def update_position(self, symbol, current_price):
        """Update position with current price and calculate P&L"""
        if symbol not in self.positions:
            return None

        position = self.positions[symbol]
        position['current_price'] = current_price

        # Calculate unrealized P&L
        if position['direction'] == 'LONG':
            pnl = (current_price - position['entry_price']) * position['quantity']
        else:  # SHORT
            pnl = (position['entry_price'] - current_price) * position['quantity']

        position['unrealized_pnl'] = pnl
        position['unrealized_pnl_pct'] = (pnl / position['position_value']) * 100

        # Check stop loss / take profit
        should_close = False
        close_reason = None

        if position['stop_loss'] and position['direction'] == 'LONG' and current_price <= position['stop_loss']:
            should_close = True
            close_reason = 'STOP_LOSS'
        elif position['stop_loss'] and position['direction'] == 'SHORT' and current_price >= position['stop_loss']:
            should_close = True
            close_reason = 'STOP_LOSS'
        elif position['take_profit'] and position['direction'] == 'LONG' and current_price >= position['take_profit']:
            should_close = True
            close_reason = 'TAKE_PROFIT'
        elif position['take_profit'] and position['direction'] == 'SHORT' and current_price <= position['take_profit']:
            should_close = True
            close_reason = 'TAKE_PROFIT'

        return {
            'position': position,
            'should_close': should_close,
            'close_reason': close_reason
        }

    def close_position(self, symbol, exit_price, reason='MANUAL'):
        """
        Close an existing position

        Args:
            symbol: Trading pair
            exit_price: Exit price
            reason: Reason for closing (STOP_LOSS, TAKE_PROFIT, MANUAL, etc.)

        Returns:
            Trade result
        """
        if symbol not in self.positions:
            logger.warning(f"No open position for {symbol}")
            return None

        position = self.positions[symbol]

        # Calculate realized P&L
        if position['direction'] == 'LONG':
            pnl = (exit_price - position['entry_price']) * position['quantity']
        else:  # SHORT
            pnl = (position['entry_price'] - exit_price) * position['quantity']

        pnl_pct = (pnl / position['position_value']) * 100

        # Update balance
        self.balance += pnl
        self.reserved_capital -= position['position_value']

        # Create trade record
        trade = {
            'symbol': symbol,
            'direction': position['direction'],
            'entry_price': position['entry_price'],
            'exit_price': exit_price,
            'quantity': position['quantity'],
            'pnl': pnl,
            'pnl_pct': pnl_pct,
            'entry_time': position['entry_time'],
            'exit_time': datetime.now().isoformat(),
            'reason': reason,
            'duration': None  # Could calculate this
        }

        self.trade_history.append(trade)

        logger.info(f"Closed {position['direction']} position for {symbol} at ${exit_price:.8f}, "
                   f"P&L: ${pnl:.2f} ({pnl_pct:.2f}%), Reason: {reason}")

        # Remove position
        del self.positions[symbol]

        return trade

    def get_portfolio_stats(self):
        """Get portfolio statistics"""
        total_unrealized_pnl = sum(p['unrealized_pnl'] for p in self.positions.values())
        total_value = self.balance + total_unrealized_pnl

        # Calculate win rate and stats from trade history
        if self.trade_history:
            winning_trades = [t for t in self.trade_history if t['pnl'] > 0]
            losing_trades = [t for t in self.trade_history if t['pnl'] < 0]

            win_rate = len(winning_trades) / len(self.trade_history) * 100
            avg_win = sum(t['pnl'] for t in winning_trades) / len(winning_trades) if winning_trades else 0
            avg_loss = sum(t['pnl'] for t in losing_trades) / len(losing_trades) if losing_trades else 0
            total_trades = len(self.trade_history)
            total_profit = sum(t['pnl'] for t in self.trade_history)
        else:
            win_rate = 0
            avg_win = 0
            avg_loss = 0
            total_trades = 0
            total_profit = 0

        return {
            'balance': self.balance,
            'reserved_capital': self.reserved_capital,
            'available_capital': self.get_available_capital(),
            'total_unrealized_pnl': total_unrealized_pnl,
            'total_value': total_value,
            'total_return': ((total_value - self.initial_balance) / self.initial_balance) * 100,
            'open_positions': len(self.positions),
            'max_positions': self.max_positions,
            'total_trades': total_trades,
            'win_rate': win_rate,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'total_profit': total_profit,
            'positions': list(self.positions.values())
        }

    def get_recent_trade_history(self, hours=24):
        """
        Get recent trade history from the last N hours

        Args:
            hours: Number of hours to look back (default: 24)

        Returns:
            List of recent trades, sorted by exit_time (newest first)
        """
        from datetime import datetime, timedelta

        if not self.trade_history:
            return []

        cutoff_time = datetime.now() - timedelta(hours=hours)

        # Filter trades from the last N hours
        recent_trades = []
        for trade in self.trade_history:
            try:
                exit_time = datetime.fromisoformat(trade['exit_time'])
                if exit_time >= cutoff_time:
                    recent_trades.append(trade)
            except (ValueError, KeyError):
                # Skip trades with invalid timestamps
                continue

        # Sort by exit_time, newest first
        recent_trades.sort(key=lambda t: t['exit_time'], reverse=True)

        return recent_trades

    def get_position(self, symbol):
        """Get position info for a symbol"""
        return self.positions.get(symbol)

    def get_all_positions(self):
        """Get all open positions"""
        return list(self.positions.values())

    def close_all_positions(self, current_prices):
        """
        Close all open positions

        Args:
            current_prices: Dict of {symbol: price}
        """
        for symbol in list(self.positions.keys()):
            price = current_prices.get(symbol)
            if price:
                self.close_position(symbol, price, reason='CLOSE_ALL')

    def reset(self):
        """Reset portfolio to initial state"""
        self.balance = self.initial_balance
        self.positions = {}
        self.trade_history = []
        self.reserved_capital = 0
        logger.info("Portfolio reset to initial state")
