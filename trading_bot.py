"""
Main trading bot - runs live or paper trading
"""
import time
import signal
import sys
from datetime import datetime
from binance_client import BinanceClient
from strategies import StrategyFactory
from risk_management import RiskManager
from indicators import TechnicalIndicators
from config import Config


class TradingBot:
    """Main trading bot that executes strategies"""

    def __init__(self):
        """Initialize trading bot"""
        # Validate configuration
        Config.validate()

        # Initialize components
        self.client = BinanceClient(
            api_key=Config.BINANCE_API_KEY if Config.TRADING_MODE == 'live' else None,
            api_secret=Config.BINANCE_API_SECRET if Config.TRADING_MODE == 'live' else None,
            paper_trading=(Config.TRADING_MODE == 'paper')
        )

        self.strategy = StrategyFactory.get_strategy(
            Config.STRATEGY,
            rsi_period=Config.RSI_PERIOD,
            rsi_oversold=Config.RSI_OVERSOLD,
            rsi_overbought=Config.RSI_OVERBOUGHT
        )

        self.risk_manager = RiskManager(
            max_positions=Config.MAX_POSITIONS,
            risk_per_trade=Config.RISK_PER_TRADE,
            stop_loss_percent=Config.STOP_LOSS_PERCENT,
            take_profit_percent=Config.TAKE_PROFIT_PERCENT
        )

        self.running = True
        self.starting_balance = self.client.get_account_balance()

        # Setup graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)

    def _signal_handler(self, sig, frame):
        """Handle Ctrl+C gracefully"""
        print("\n\n⚠️  Shutting down bot...")
        self.running = False

    def run(self, interval: str = '15m', sleep_time: int = 60):
        """
        Run the trading bot

        Args:
            interval: Timeframe for analysis ('1m', '5m', '15m', '1h', '4h', '1d')
            sleep_time: Time to sleep between iterations (seconds)
        """
        mode = "PAPER TRADING" if Config.TRADING_MODE == 'paper' else "LIVE TRADING"

        print(f"\n{'='*60}")
        print(f"🤖 CRYPTO TRADING BOT STARTED - {mode}")
        print(f"{'='*60}")
        print(f"Symbol:       {Config.TRADE_SYMBOL}")
        print(f"Strategy:     {self.strategy.name}")
        print(f"Interval:     {interval}")
        print(f"Balance:      ${self.starting_balance:.2f}")
        print(f"Max Risk:     {Config.RISK_PER_TRADE*100}% per trade")
        print(f"{'='*60}\n")

        iteration = 0

        while self.running:
            try:
                iteration += 1
                print(f"\n--- Iteration {iteration} | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---")

                # Get historical data
                df = self.client.get_historical_klines(
                    symbol=Config.TRADE_SYMBOL,
                    interval=interval,
                    limit=500
                )

                if df.empty:
                    print("⚠️  Failed to fetch market data")
                    time.sleep(sleep_time)
                    continue

                # Add indicators
                df = TechnicalIndicators.add_all_indicators(df)

                # Get current price
                current_price = self.client.get_current_price(Config.TRADE_SYMBOL)
                print(f"Current Price: ${current_price:,.2f}")

                # Get current balance and positions
                balance = self.client.get_account_balance()
                positions = self.client.get_open_positions()

                print(f"Balance: ${balance:.2f} | Open Positions: {len(positions)}/{Config.MAX_POSITIONS}")

                # Check risk limits
                if not self.risk_manager.check_daily_loss_limit(balance, self.starting_balance):
                    print("⚠️  Daily loss limit reached. Stopping for today.")
                    break

                if not self.risk_manager.check_drawdown_limit(balance):
                    print("⚠️  Max drawdown reached. Stopping trading.")
                    break

                # Check existing positions for exit
                for position in positions:
                    should_exit, reason = self.risk_manager.should_exit_position(
                        position,
                        current_price
                    )

                    if should_exit:
                        print(f"\n🔴 Exiting position: {reason}")
                        self._close_position(position, current_price)

                # Get strategy signal
                action, confidence = self.strategy.analyze(df)

                print(f"Strategy Signal: {action} (confidence: {confidence:.2%})")

                # Execute trades based on signal
                if action == 'BUY' and confidence > 0.6:
                    if self.risk_manager.can_open_position(positions):
                        print(f"\n🟢 Opening BUY position (confidence: {confidence:.2%})")
                        self._open_position(current_price)
                    else:
                        print(f"⚠️  Max positions reached. Cannot open new position.")

                elif action == 'SELL' and len(positions) > 0:
                    print(f"\n🔴 Closing all positions (strategy signal)")
                    for position in positions:
                        self._close_position(position, current_price)

                # Display performance
                self._display_performance()

                # Sleep before next iteration
                print(f"\nSleeping for {sleep_time} seconds...")
                time.sleep(sleep_time)

            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"❌ Error: {e}")
                import traceback
                traceback.print_exc()
                time.sleep(sleep_time)

        # Cleanup
        self._shutdown()

    def _open_position(self, current_price: float):
        """Open a new position"""
        balance = self.client.get_account_balance()

        # Calculate position size
        position_size = self.risk_manager.calculate_position_size(
            balance,
            current_price
        )

        # Calculate quantity (round to appropriate precision)
        # For BTC, use 5 decimal places
        quantity = round(position_size, 5)

        if quantity * current_price < 10:  # Minimum order size
            print(f"⚠️  Position too small (${quantity * current_price:.2f}). Minimum $10.")
            return

        # Place order
        order = self.client.place_order(
            symbol=Config.TRADE_SYMBOL,
            side='BUY',
            quantity=quantity
        )

        if order:
            print(f"✅ Position opened: {quantity} @ ${current_price:.2f}")

    def _close_position(self, position: dict, current_price: float):
        """Close an existing position"""
        order = self.client.place_order(
            symbol=Config.TRADE_SYMBOL,
            side='SELL',
            quantity=position['quantity']
        )

        if order:
            print(f"✅ Position closed: {position['quantity']} @ ${current_price:.2f}")

    def _display_performance(self):
        """Display current performance statistics"""
        portfolio_value = self.client.get_portfolio_value(Config.TRADE_SYMBOL)
        total_return = ((portfolio_value - self.starting_balance) / self.starting_balance) * 100

        print(f"\n📊 Performance:")
        print(f"   Portfolio Value: ${portfolio_value:.2f}")
        print(f"   Total Return: {total_return:+.2f}%")

        # Get performance summary from risk manager
        perf = self.risk_manager.get_performance_summary()
        if perf['total_trades'] > 0:
            print(f"   Total Trades: {perf['total_trades']}")
            print(f"   Win Rate: {perf['win_rate']:.1f}%")
            print(f"   Total PnL: ${perf['total_pnl']:+.2f}")

    def _shutdown(self):
        """Shutdown bot and display final results"""
        print(f"\n{'='*60}")
        print(f"🛑 BOT STOPPED")
        print(f"{'='*60}")

        final_balance = self.client.get_account_balance()
        portfolio_value = self.client.get_portfolio_value(Config.TRADE_SYMBOL)
        total_return = ((portfolio_value - self.starting_balance) / self.starting_balance) * 100

        print(f"Starting Balance: ${self.starting_balance:.2f}")
        print(f"Final Portfolio:  ${portfolio_value:.2f}")
        print(f"Total Return:     {total_return:+.2f}%")

        perf = self.risk_manager.get_performance_summary()
        if perf['total_trades'] > 0:
            print(f"\nTrade Summary:")
            print(f"Total Trades:     {perf['total_trades']}")
            print(f"Win Rate:         {perf['win_rate']:.1f}%")
            print(f"Total PnL:        ${perf['total_pnl']:+.2f}")

        print(f"{'='*60}\n")


if __name__ == '__main__':
    bot = TradingBot()
    bot.run(interval='15m', sleep_time=60)
