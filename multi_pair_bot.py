"""
Multi-Pair Trading Bot - Scans and trades multiple pairs simultaneously
"""
import time
import logging
from datetime import datetime
from market_scanner import MarketScanner
from portfolio_manager import PortfolioManager
from binance_client import BinanceClient
from risk_management import RiskManager
from ai_advisor import AITradingAdvisor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MultiPairBot:
    """Trading bot that monitors and trades multiple pairs"""

    def __init__(self, config):
        """
        Initialize multi-pair bot

        Args:
            config: Configuration dict with settings
        """
        self.config = config
        self.running = False

        # Selected pairs to trade (if provided)
        self.selected_pairs = config.get('selected_pairs', [])

        # Initialize components
        self.scanner = MarketScanner(
            quote_currency=config.get('QUOTE_CURRENCY', 'USDT'),
            min_volume_usdt=config.get('MIN_VOLUME_USDT', 1000000),
            max_pairs=config.get('MAX_PAIRS_TO_SCAN', 100)
        )

        self.portfolio = PortfolioManager(
            initial_balance=config.get('INITIAL_BALANCE', 10000),
            max_positions=config.get('MAX_POSITIONS', 5),
            max_allocation_per_trade=config.get('MAX_ALLOCATION_PER_TRADE', 0.20)
        )

        self.client = BinanceClient()
        self.risk_manager = RiskManager(config)
        self.ai_advisor = AITradingAdvisor()

        # Settings
        self.scan_interval = config.get('SCAN_INTERVAL', 300)  # 5 minutes
        self.min_opportunity_score = config.get('MIN_OPPORTUNITY_SCORE', 65)
        self.trading_mode = config.get('TRADING_MODE', 'paper')
        self.stop_loss_pct = config.get('STOP_LOSS_PCT', 0.02)
        self.take_profit_pct = config.get('TAKE_PROFIT_PCT', 0.04)
        self.use_ai = config.get('USE_AI', True)  # Enable AI by default

        self.last_scan_time = 0
        self.scan_count = 0

        # Loss cooldown system - prevents immediate re-entry on losing trades
        self.loss_cooldown = {}  # {symbol: timestamp}
        self.cooldown_duration = config.get('LOSS_COOLDOWN_MINUTES', 30) * 60  # Convert to seconds

    def scan_for_opportunities(self):
        """Scan market for new opportunities"""
        print("\n" + "="*80)
        print(f"🔍 SCANNING MARKET (Scan #{self.scan_count + 1})")
        print("="*80)

        # If specific pairs were selected, only scan those
        if self.selected_pairs:
            print(f"📋 Scanning {len(self.selected_pairs)} MANUALLY SELECTED pairs: {', '.join(self.selected_pairs)}")
            logger.info(f"Scanning {len(self.selected_pairs)} selected pairs...")
            opportunities = []
            for symbol in self.selected_pairs:
                opp = self.scanner.analyze_pair(symbol, timeframe=self.config.get('TIMEFRAME', '15m'))
                if opp and opp['score'] >= self.min_opportunity_score:
                    opportunities.append(opp)
                    print(f"  ✓ {symbol}: Score={opp['score']}, Direction={opp.get('direction', 'NONE')}, Price=${opp['price']:.2f}")
            # Sort by score
            opportunities.sort(key=lambda x: x['score'], reverse=True)
        else:
            # Scan all pairs
            print(f"📊 Scanning ALL market pairs (min score: {self.min_opportunity_score})")
            opportunities = self.scanner.scan_market(
                timeframe=self.config.get('TIMEFRAME', '15m'),
                min_score=self.min_opportunity_score
            )

        self.last_scan_time = time.time()
        self.scan_count += 1

        print(f"\n📈 Found {len(opportunities)} opportunities")
        return opportunities

    def evaluate_opportunity(self, opportunity):
        """
        Evaluate if we should enter a trade for this opportunity

        Args:
            opportunity: Opportunity dict from scanner

        Returns:
            True if should trade, False otherwise
        """
        symbol = opportunity['symbol']

        # Check if already have position
        if symbol in self.portfolio.positions:
            return False

        # Check portfolio capacity
        if not self.portfolio.can_open_position(symbol):
            return False

        # Check loss cooldown (only for non-manual pairs)
        if symbol in self.loss_cooldown:
            time_since_loss = time.time() - self.loss_cooldown[symbol]
            if time_since_loss < self.cooldown_duration:
                remaining_min = (self.cooldown_duration - time_since_loss) / 60
                print(f"   ⏳ {symbol} in cooldown for {remaining_min:.1f} more minutes (previous loss)")
                logger.info(f"{symbol} skipped - in cooldown for {remaining_min:.1f} more minutes")
                return False
            else:
                # Cooldown expired, remove from dict
                del self.loss_cooldown[symbol]
                print(f"   ✅ {symbol} cooldown expired, can trade again")
                logger.info(f"{symbol} cooldown expired")

        # Check if this is a manually selected pair
        is_manual_selection = self.selected_pairs and symbol in self.selected_pairs

        if is_manual_selection:
            print(f"\n🎯 MANUAL SELECTION: {symbol}")
            logger.info(f"✓ MANUAL SELECTION: {symbol}")
            # Ensure it has a direction for trade execution
            if not opportunity['direction']:
                # Force a direction based on price momentum or just default to LONG
                opportunity['direction'] = 'LONG'
                print(f"   ➤ Setting default direction: LONG")
                logger.info(f"  Setting default direction: LONG")

        # For non-manual pairs, use normal checks
        if not is_manual_selection:
            # Check opportunity score
            if opportunity['score'] < self.min_opportunity_score:
                return False

            # Check if has clear direction
            if not opportunity['direction']:
                return False

        # Use AI advisor for additional validation (if enabled)
        if self.use_ai:
            try:
                if is_manual_selection:
                    print(f"\n🤖 AI ANALYZING (MANUAL OVERRIDE): {symbol}...")
                else:
                    print(f"\n🤖 AI ANALYZING: {symbol}...")

                ai_analysis = self.ai_advisor.analyze_opportunity(opportunity)

                # For manual selections, log AI opinion but proceed anyway
                if is_manual_selection:
                    if not ai_analysis['should_trade']:
                        print(f"   ⚠️  AI CAUTION: {symbol} (proceeding anyway - manual selection)")
                        print(f"      AI Reason: {ai_analysis['reasoning'][:100]}...")
                        print(f"      Confidence: {ai_analysis['confidence']:.0%}, Risk: {ai_analysis['risk_assessment'].upper()}")
                        logger.info(f"AI cautioned {symbol} but proceeding (manual override): {ai_analysis['reasoning']}")
                    else:
                        print(f"   ✅ AI APPROVED: {symbol}")
                        print(f"      Confidence: {ai_analysis['confidence']:.0%}, Risk: {ai_analysis['risk_assessment'].upper()}")
                        logger.info(f"AI approved {symbol} (confidence: {ai_analysis['confidence']:.0%}, risk: {ai_analysis['risk_assessment']})")
                else:
                    # For non-manual pairs, AI must approve the trade
                    if not ai_analysis['should_trade']:
                        print(f"   ❌ AI REJECTED: {symbol}")
                        print(f"      Reason: {ai_analysis['reasoning'][:100]}...")
                        print(f"      Confidence: {ai_analysis['confidence']:.0%}, Risk: {ai_analysis['risk_assessment'].upper()}")
                        logger.info(f"AI rejected {symbol}: {ai_analysis['reasoning']}")
                        return False

                    # Log AI recommendation
                    print(f"   ✅ AI APPROVED: {symbol}")
                    print(f"      Confidence: {ai_analysis['confidence']:.0%}, Risk: {ai_analysis['risk_assessment'].upper()}")
                    logger.info(f"AI approved {symbol} (confidence: {ai_analysis['confidence']:.0%}, risk: {ai_analysis['risk_assessment']})")

                # Store AI analysis for logging
                opportunity['ai_analysis'] = ai_analysis

            except Exception as e:
                print(f"   ⚠️  AI ANALYSIS FAILED for {symbol}: {e}")
                logger.warning(f"AI analysis failed for {symbol}, using technical score only: {e}")
                # Continue without AI if it fails (or if manual selection)

        return True

    def calculate_entry_params(self, opportunity):
        """
        Calculate entry parameters for a trade

        Args:
            opportunity: Opportunity dict

        Returns:
            dict with entry parameters
        """
        symbol = opportunity['symbol']
        price = opportunity['price']
        direction = opportunity['direction']

        # Calculate position size
        position_size = self.portfolio.calculate_position_size(
            symbol=symbol,
            price=price,
            direction=direction
        )

        # Calculate stop loss and take profit
        if direction == 'LONG':
            stop_loss = price * (1 - self.stop_loss_pct)
            take_profit = price * (1 + self.take_profit_pct)
        else:  # SHORT
            stop_loss = price * (1 + self.stop_loss_pct)
            take_profit = price * (1 - self.take_profit_pct)

        params = {
            'symbol': symbol,
            'direction': direction,
            'entry_price': price,
            'quantity': position_size['quantity'],
            'stop_loss': stop_loss,
            'take_profit': take_profit,
            'score': opportunity['score'],
            'signals': opportunity['signals']
        }

        # Include AI analysis if it exists
        if 'ai_analysis' in opportunity:
            params['ai_analysis'] = opportunity['ai_analysis']

        return params

    def execute_trade(self, params):
        """
        Execute a trade (paper or live)

        Args:
            params: Trade parameters

        Returns:
            Position info or None
        """
        symbol = params['symbol']

        print("\n" + "="*80)
        print(f"💰 EXECUTING TRADE: {symbol}")
        print("="*80)
        print(f"   Direction:    {params['direction']}")
        print(f"   Entry Price:  ${params['entry_price']:.8f}")
        print(f"   Quantity:     {params['quantity']:.8f}")
        print(f"   Stop Loss:    ${params['stop_loss']:.8f} (-{((params['entry_price'] - params['stop_loss']) / params['entry_price'] * 100):.1f}%)")
        print(f"   Take Profit:  ${params['take_profit']:.8f} (+{((params['take_profit'] - params['entry_price']) / params['entry_price'] * 100):.1f}%)")
        print(f"   Tech Score:   {params['score']}/100")
        print(f"   Signals:      {', '.join(params['signals'])}")
        print("="*80)

        logger.info(f"\n{'='*60}")
        logger.info(f"EXECUTING TRADE: {symbol}")
        logger.info(f"Direction: {params['direction']}")
        logger.info(f"Entry: ${params['entry_price']:.8f}")
        logger.info(f"Quantity: {params['quantity']:.8f}")
        logger.info(f"Stop Loss: ${params['stop_loss']:.8f}")
        logger.info(f"Take Profit: ${params['take_profit']:.8f}")
        logger.info(f"Score: {params['score']}/100")
        logger.info(f"Signals: {', '.join(params['signals'])}")
        logger.info(f"{'='*60}\n")

        if self.trading_mode == 'paper':
            # Paper trading - just update portfolio
            position = self.portfolio.open_position(
                symbol=symbol,
                direction=params['direction'],
                entry_price=params['entry_price'],
                quantity=params['quantity'],
                stop_loss=params['stop_loss'],
                take_profit=params['take_profit'],
                ai_analysis=params.get('ai_analysis'),
                opportunity_data=params
            )
            return position

        else:
            # Live trading - execute on Binance
            try:
                # Place market order
                if params['direction'] == 'LONG':
                    order = self.client.place_order(
                        symbol=symbol,
                        side='BUY',
                        order_type='MARKET',
                        quantity=params['quantity']
                    )
                else:  # SHORT - would need futures/margin account
                    logger.error("SHORT positions require futures/margin account")
                    return None

                if order:
                    # Set stop loss and take profit orders
                    # ... implement OCO order or separate stop/limit orders
                    position = self.portfolio.open_position(
                        symbol=symbol,
                        direction=params['direction'],
                        entry_price=order['fills'][0]['price'],
                        quantity=params['quantity'],
                        stop_loss=params['stop_loss'],
                        take_profit=params['take_profit']
                    )
                    return position

            except Exception as e:
                logger.error(f"Error executing trade: {e}")
                return None

    def update_positions(self):
        """Update all open positions with current prices"""
        if not self.portfolio.positions:
            return

        symbols = list(self.portfolio.positions.keys())
        positions_to_close = []

        for symbol in symbols:
            try:
                # Get current price
                ticker = self.client.client.get_symbol_ticker(symbol=symbol)
                current_price = float(ticker['price'])

                # Update position
                result = self.portfolio.update_position(symbol, current_price)

                if result and result['should_close']:
                    positions_to_close.append({
                        'symbol': symbol,
                        'price': current_price,
                        'reason': result['close_reason']
                    })

            except Exception as e:
                logger.error(f"Error updating position {symbol}: {e}")

        # Close positions that hit stop/target
        for close_info in positions_to_close:
            symbol = close_info['symbol']
            print(f"\n🚪 CLOSING POSITION: {symbol}")
            print(f"   Reason: {close_info['reason']}")
            print(f"   Exit Price: ${close_info['price']:.2f}")

            closed_position = self.portfolio.close_position(
                symbol=symbol,
                exit_price=close_info['price'],
                reason=close_info['reason']
            )

            # Add to cooldown if it was a loss
            if closed_position and closed_position.get('pnl', 0) < 0:
                self.loss_cooldown[symbol] = time.time()
                cooldown_min = self.cooldown_duration / 60
                print(f"   ⏳ {symbol} added to cooldown for {cooldown_min:.0f} minutes (loss detected)")
                logger.info(f"{symbol} added to cooldown for {cooldown_min:.0f} minutes due to loss")

    def run_cycle(self):
        """Run one complete bot cycle"""
        # Update existing positions
        self.update_positions()

        # Check if should scan for new opportunities
        time_since_scan = time.time() - self.last_scan_time
        if time_since_scan >= self.scan_interval:

            # Scan market
            opportunities = self.scan_for_opportunities()

            if opportunities:
                logger.info(f"Found {len(opportunities)} opportunities")

                # Evaluate and trade top opportunities
                for opp in opportunities[:3]:  # Look at top 3
                    if self.evaluate_opportunity(opp):
                        params = self.calculate_entry_params(opp)
                        self.execute_trade(params)

                        # Small delay between trades
                        time.sleep(1)

        # Log portfolio stats
        stats = self.portfolio.get_portfolio_stats()
        pnl = stats['total_value'] - stats['balance']
        pnl_emoji = "📈" if pnl > 0 else "📉" if pnl < 0 else "➖"

        print(f"\n{pnl_emoji} Portfolio: ${stats['total_value']:.2f} | "
              f"P&L: ${pnl:.2f} ({stats['total_return']:.2f}%) | "
              f"Positions: {stats['open_positions']}/{stats['max_positions']}")

        logger.info(f"\nPortfolio: ${stats['total_value']:.2f} | "
                   f"P&L: ${stats['total_value'] - stats['balance']:.2f} "
                   f"({stats['total_return']:.2f}%) | "
                   f"Positions: {stats['open_positions']}/{stats['max_positions']}")

    def start(self):
        """Start the bot"""
        logger.info("="*80)
        logger.info("MULTI-PAIR TRADING BOT STARTING")
        logger.info("="*80)
        logger.info(f"Mode: {self.trading_mode.upper()}")
        logger.info(f"Quote Currency: {self.scanner.quote_currency}")
        logger.info(f"Max Positions: {self.portfolio.max_positions}")
        logger.info(f"Initial Balance: ${self.portfolio.initial_balance:,.2f}")
        logger.info(f"Min Opportunity Score: {self.min_opportunity_score}")
        logger.info(f"Scan Interval: {self.scan_interval}s")
        logger.info("="*80 + "\n")

        self.running = True

        try:
            while self.running:
                self.run_cycle()
                time.sleep(10)  # Check every 10 seconds

        except KeyboardInterrupt:
            logger.info("\nBot stopped by user")
            self.stop()

    def stop(self):
        """Stop the bot and close all positions"""
        self.running = False

        # Close all open positions before stopping
        if self.portfolio.positions:
            logger.info("\n" + "="*80)
            logger.info("CLOSING ALL POSITIONS")
            logger.info("="*80)

            # Get current prices for all open positions
            current_prices = {}
            for symbol in self.portfolio.positions.keys():
                try:
                    price = self.client.get_current_price(symbol)
                    current_prices[symbol] = price
                    logger.info(f"Closing {symbol} at ${price}")
                except Exception as e:
                    logger.error(f"Failed to get price for {symbol}: {e}")

            # Close all positions
            self.portfolio.close_all_positions(current_prices)

        # Show final stats
        stats = self.portfolio.get_portfolio_stats()
        logger.info("\n" + "="*80)
        logger.info("FINAL PORTFOLIO STATS")
        logger.info("="*80)
        logger.info(f"Initial Balance: ${self.portfolio.initial_balance:,.2f}")
        logger.info(f"Final Balance: ${stats['balance']:,.2f}")
        logger.info(f"Total Value: ${stats['total_value']:,.2f}")
        logger.info(f"Total Return: {stats['total_return']:.2f}%")
        logger.info(f"Total Trades: {stats['total_trades']}")
        logger.info(f"Win Rate: {stats['win_rate']:.1f}%")
        logger.info(f"Open Positions: {stats['open_positions']}")
        logger.info("="*80)

    def get_status(self):
        """Get current bot status"""
        stats = self.portfolio.get_portfolio_stats()
        opportunities = self.scanner.get_top_opportunities(5)

        return {
            'running': self.running,
            'mode': self.trading_mode,
            'scan_count': self.scan_count,
            'last_scan': datetime.fromtimestamp(self.last_scan_time).isoformat() if self.last_scan_time else None,
            'portfolio': stats,
            'top_opportunities': opportunities,
            'config': {
                'quote_currency': self.scanner.quote_currency,
                'max_positions': self.portfolio.max_positions,
                'min_score': self.min_opportunity_score,
                'scan_interval': self.scan_interval
            }
        }


if __name__ == '__main__':
    # Test configuration
    config = {
        'QUOTE_CURRENCY': 'USDT',
        'MIN_VOLUME_USDT': 2000000,
        'MAX_PAIRS_TO_SCAN': 50,
        'INITIAL_BALANCE': 10000,
        'MAX_POSITIONS': 3,
        'MAX_ALLOCATION_PER_TRADE': 0.25,
        'SCAN_INTERVAL': 180,  # 3 minutes
        'MIN_OPPORTUNITY_SCORE': 70,
        'TRADING_MODE': 'paper',
        'TIMEFRAME': '15m',
        'STOP_LOSS_PCT': 0.02,
        'TAKE_PROFIT_PCT': 0.04,
        'RISK_PER_TRADE': 0.02
    }

    bot = MultiPairBot(config)
    bot.start()
