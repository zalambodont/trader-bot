"""
Binance API client wrapper with paper trading support
"""
from binance.client import Client
from binance.exceptions import BinanceAPIException
from datetime import datetime
import pandas as pd
from typing import Optional, Dict, List
from config import Config


class BinanceClient:
    """Wrapper for Binance API with paper trading mode"""

    def __init__(self, api_key: str = None, api_secret: str = None, paper_trading: bool = True):
        """
        Initialize Binance client

        Args:
            api_key: Binance API key
            api_secret: Binance API secret
            paper_trading: If True, simulate trades without executing them
        """
        self.paper_trading = paper_trading
        self.paper_balance = {'USDT': 10000.0}  # Start with $10,000 in paper trading
        self.paper_positions = []

        # Only connect to Binance if we have credentials (needed for market data)
        if api_key and api_secret:
            try:
                self.client = Client(api_key, api_secret)
                # Test the connection
                self.client.ping()
                print("✓ Connected to Binance API")
            except BinanceAPIException as e:
                print(f"✗ Failed to connect to Binance: {e}")
                self.client = None
        else:
            # For paper trading, we can use public API (no credentials needed)
            self.client = Client("", "")
            print("✓ Using Binance public API (paper trading mode)")

    def get_current_price(self, symbol: str) -> float:
        """Get current price for a symbol"""
        try:
            ticker = self.client.get_symbol_ticker(symbol=symbol)
            return float(ticker['price'])
        except Exception as e:
            print(f"Error getting price for {symbol}: {e}")
            return 0.0

    def get_historical_klines(self, symbol: str, interval: str, limit: int = 500) -> pd.DataFrame:
        """
        Get historical candlestick data

        Args:
            symbol: Trading pair (e.g., 'BTCUSDT')
            interval: Timeframe (e.g., '1m', '5m', '15m', '1h', '4h', '1d')
            limit: Number of candles to fetch

        Returns:
            DataFrame with OHLCV data
        """
        try:
            klines = self.client.get_klines(symbol=symbol, interval=interval, limit=limit)

            df = pd.DataFrame(klines, columns=[
                'timestamp', 'open', 'high', 'low', 'close', 'volume',
                'close_time', 'quote_volume', 'trades', 'taker_buy_base',
                'taker_buy_quote', 'ignore'
            ])

            # Convert to proper types
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            for col in ['open', 'high', 'low', 'close', 'volume']:
                df[col] = df[col].astype(float)

            df.set_index('timestamp', inplace=True)
            return df[['open', 'high', 'low', 'close', 'volume']]

        except Exception as e:
            print(f"Error fetching historical data: {e}")
            return pd.DataFrame()

    def get_account_balance(self, asset: str = 'USDT') -> float:
        """Get account balance for a specific asset"""
        if self.paper_trading:
            return self.paper_balance.get(asset, 0.0)

        try:
            balance = self.client.get_asset_balance(asset=asset)
            return float(balance['free']) if balance else 0.0
        except Exception as e:
            print(f"Error getting balance: {e}")
            return 0.0

    def place_order(self, symbol: str, side: str, quantity: float, order_type: str = 'MARKET') -> Optional[Dict]:
        """
        Place an order (or simulate in paper trading)

        Args:
            symbol: Trading pair (e.g., 'BTCUSDT')
            side: 'BUY' or 'SELL'
            quantity: Amount to trade
            order_type: Order type (default: 'MARKET')

        Returns:
            Order information dict or None if failed
        """
        current_price = self.get_current_price(symbol)

        if self.paper_trading:
            # Simulate the order
            order_value = quantity * current_price

            if side == 'BUY':
                usdt_balance = self.paper_balance.get('USDT', 0)
                if usdt_balance < order_value:
                    print(f"✗ Insufficient balance. Need ${order_value:.2f}, have ${usdt_balance:.2f}")
                    return None

                # Deduct USDT and add position
                self.paper_balance['USDT'] -= order_value
                self.paper_positions.append({
                    'symbol': symbol,
                    'side': side,
                    'quantity': quantity,
                    'entry_price': current_price,
                    'timestamp': datetime.now(),
                    'value': order_value
                })

                print(f"✓ PAPER TRADE: BUY {quantity} {symbol} @ ${current_price:.2f} = ${order_value:.2f}")
                print(f"  Remaining balance: ${self.paper_balance['USDT']:.2f}")

            elif side == 'SELL':
                # Find and close position
                for i, pos in enumerate(self.paper_positions):
                    if pos['symbol'] == symbol and pos['side'] == 'BUY':
                        exit_value = pos['quantity'] * current_price
                        profit = exit_value - pos['value']
                        profit_pct = (profit / pos['value']) * 100

                        self.paper_balance['USDT'] += exit_value
                        self.paper_positions.pop(i)

                        print(f"✓ PAPER TRADE: SELL {quantity} {symbol} @ ${current_price:.2f} = ${exit_value:.2f}")
                        print(f"  Profit: ${profit:.2f} ({profit_pct:+.2f}%)")
                        print(f"  New balance: ${self.paper_balance['USDT']:.2f}")
                        break

            return {
                'symbol': symbol,
                'side': side,
                'quantity': quantity,
                'price': current_price,
                'timestamp': datetime.now(),
                'paper_trade': True
            }

        else:
            # Execute real trade
            try:
                print(f"⚠️  LIVE TRADE: {side} {quantity} {symbol}")
                order = self.client.create_order(
                    symbol=symbol,
                    side=side,
                    type=order_type,
                    quantity=quantity
                )
                print(f"✓ Order executed: {order}")
                return order

            except BinanceAPIException as e:
                print(f"✗ Order failed: {e}")
                return None

    def get_open_positions(self) -> List[Dict]:
        """Get all open positions"""
        if self.paper_trading:
            return self.paper_positions

        # For live trading, implement position tracking
        # This is a simplified version
        return []

    def get_portfolio_value(self, symbol: str = 'BTCUSDT') -> float:
        """Calculate total portfolio value"""
        total = self.paper_balance.get('USDT', 0)

        for pos in self.paper_positions:
            if pos['symbol'] == symbol:
                current_price = self.get_current_price(symbol)
                total += pos['quantity'] * current_price

        return total
