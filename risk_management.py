"""
Risk management module for trading bot
"""
from typing import Dict, List, Optional
from datetime import datetime, timedelta


class RiskManager:
    """Manages trading risk and position sizing"""

    def __init__(
        self,
        max_positions: int = 3,
        risk_per_trade: float = 0.02,
        max_daily_loss: float = 0.05,
        max_drawdown: float = 0.20,
        stop_loss_percent: float = 2.0,
        take_profit_percent: float = 5.0
    ):
        """
        Initialize risk manager

        Args:
            max_positions: Maximum number of concurrent positions
            risk_per_trade: Maximum risk per trade as % of capital (0.02 = 2%)
            max_daily_loss: Maximum daily loss before stopping (0.05 = 5%)
            max_drawdown: Maximum drawdown before stopping (0.20 = 20%)
            stop_loss_percent: Stop loss percentage (2.0 = 2%)
            take_profit_percent: Take profit percentage (5.0 = 5%)
        """
        self.max_positions = max_positions
        self.risk_per_trade = risk_per_trade
        self.max_daily_loss = max_daily_loss
        self.max_drawdown = max_drawdown
        self.stop_loss_percent = stop_loss_percent
        self.take_profit_percent = take_profit_percent

        # Track daily performance
        self.daily_pnl = {}
        self.peak_balance = None
        self.positions_history = []

    def calculate_position_size(
        self,
        balance: float,
        entry_price: float,
        stop_loss_price: Optional[float] = None
    ) -> float:
        """
        Calculate position size based on risk management

        Args:
            balance: Current account balance
            entry_price: Entry price for the trade
            stop_loss_price: Stop loss price (optional)

        Returns:
            Position size in base currency
        """
        # Calculate risk amount
        risk_amount = balance * self.risk_per_trade

        if stop_loss_price:
            # Calculate position size based on stop loss
            price_risk = abs(entry_price - stop_loss_price)
            position_size = risk_amount / price_risk
        else:
            # Use default stop loss percentage
            price_risk = entry_price * (self.stop_loss_percent / 100)
            position_size = risk_amount / price_risk

        # Ensure position doesn't exceed available balance
        max_position_value = balance / self.max_positions
        max_position_size = max_position_value / entry_price

        return min(position_size, max_position_size)

    def calculate_stop_loss(self, entry_price: float, side: str = 'BUY') -> float:
        """Calculate stop loss price"""
        if side == 'BUY':
            return entry_price * (1 - self.stop_loss_percent / 100)
        else:
            return entry_price * (1 + self.stop_loss_percent / 100)

    def calculate_take_profit(self, entry_price: float, side: str = 'BUY') -> float:
        """Calculate take profit price"""
        if side == 'BUY':
            return entry_price * (1 + self.take_profit_percent / 100)
        else:
            return entry_price * (1 - self.take_profit_percent / 100)

    def can_open_position(self, current_positions: List[Dict]) -> bool:
        """Check if we can open a new position"""
        return len(current_positions) < self.max_positions

    def check_daily_loss_limit(self, current_balance: float, starting_balance: float) -> bool:
        """
        Check if daily loss limit has been reached

        Returns:
            True if trading should continue, False if limit reached
        """
        today = datetime.now().date()

        if today not in self.daily_pnl:
            self.daily_pnl[today] = {'starting_balance': starting_balance, 'current_balance': current_balance}

        daily_loss = (current_balance - starting_balance) / starting_balance

        if daily_loss <= -self.max_daily_loss:
            print(f"⚠️  DAILY LOSS LIMIT REACHED: {daily_loss*100:.2f}%")
            print(f"   Trading suspended for today")
            return False

        return True

    def check_drawdown_limit(self, current_balance: float) -> bool:
        """
        Check if maximum drawdown has been reached

        Returns:
            True if trading should continue, False if limit reached
        """
        if self.peak_balance is None or current_balance > self.peak_balance:
            self.peak_balance = current_balance

        drawdown = (self.peak_balance - current_balance) / self.peak_balance

        if drawdown >= self.max_drawdown:
            print(f"⚠️  MAXIMUM DRAWDOWN REACHED: {drawdown*100:.2f}%")
            print(f"   Trading suspended. Please review your strategy.")
            return False

        return True

    def should_exit_position(
        self,
        position: Dict,
        current_price: float
    ) -> tuple[bool, str]:
        """
        Check if position should be exited based on stop loss or take profit

        Returns:
            Tuple of (should_exit, reason)
        """
        entry_price = position['entry_price']
        side = position['side']

        if side == 'BUY':
            pnl_percent = ((current_price - entry_price) / entry_price) * 100

            # Check stop loss
            if pnl_percent <= -self.stop_loss_percent:
                return True, f"STOP LOSS ({pnl_percent:.2f}%)"

            # Check take profit
            if pnl_percent >= self.take_profit_percent:
                return True, f"TAKE PROFIT ({pnl_percent:.2f}%)"

        return False, ""

    def get_risk_metrics(self, positions: List[Dict], balance: float) -> Dict:
        """Calculate current risk metrics"""
        total_risk = len(positions) * (balance * self.risk_per_trade)
        risk_percent = (total_risk / balance) * 100 if balance > 0 else 0

        return {
            'open_positions': len(positions),
            'max_positions': self.max_positions,
            'total_risk_amount': total_risk,
            'risk_percent': risk_percent,
            'available_slots': self.max_positions - len(positions)
        }

    def log_trade(self, trade: Dict):
        """Log trade for performance tracking"""
        self.positions_history.append({
            **trade,
            'timestamp': datetime.now()
        })

    def get_performance_summary(self) -> Dict:
        """Get performance summary"""
        if not self.positions_history:
            return {
                'total_trades': 0,
                'winning_trades': 0,
                'losing_trades': 0,
                'win_rate': 0,
                'avg_profit': 0,
                'avg_loss': 0
            }

        closed_trades = [t for t in self.positions_history if 'exit_price' in t]
        winning_trades = [t for t in closed_trades if t.get('pnl', 0) > 0]
        losing_trades = [t for t in closed_trades if t.get('pnl', 0) < 0]

        return {
            'total_trades': len(closed_trades),
            'winning_trades': len(winning_trades),
            'losing_trades': len(losing_trades),
            'win_rate': len(winning_trades) / len(closed_trades) * 100 if closed_trades else 0,
            'avg_profit': sum(t['pnl'] for t in winning_trades) / len(winning_trades) if winning_trades else 0,
            'avg_loss': sum(t['pnl'] for t in losing_trades) / len(losing_trades) if losing_trades else 0,
            'total_pnl': sum(t.get('pnl', 0) for t in closed_trades)
        }
