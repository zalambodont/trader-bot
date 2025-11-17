"""
Configuration management for the crypto trading bot
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Configuration class for trading bot settings"""

    # Binance API Credentials
    BINANCE_API_KEY = os.getenv('BINANCE_API_KEY', '')
    BINANCE_API_SECRET = os.getenv('BINANCE_API_SECRET', '')

    # Trading Mode
    TRADING_MODE = os.getenv('TRADING_MODE', 'paper').lower()

    # Trading Parameters
    TRADE_SYMBOL = os.getenv('TRADE_SYMBOL', 'BTCUSDT')
    TRADE_AMOUNT_USDT = float(os.getenv('TRADE_AMOUNT_USDT', 100))
    MAX_POSITIONS = int(os.getenv('MAX_POSITIONS', 3))
    RISK_PER_TRADE = float(os.getenv('RISK_PER_TRADE', 0.02))

    # Strategy Settings
    STRATEGY = os.getenv('STRATEGY', 'rsi_macd')
    RSI_PERIOD = int(os.getenv('RSI_PERIOD', 14))
    RSI_OVERSOLD = int(os.getenv('RSI_OVERSOLD', 30))
    RSI_OVERBOUGHT = int(os.getenv('RSI_OVERBOUGHT', 70))

    # Stop Loss and Take Profit (as percentages)
    STOP_LOSS_PERCENT = float(os.getenv('STOP_LOSS_PERCENT', 2.0))
    TAKE_PROFIT_PERCENT = float(os.getenv('TAKE_PROFIT_PERCENT', 5.0))

    @classmethod
    def validate(cls):
        """Validate configuration settings"""
        if cls.TRADING_MODE not in ['paper', 'live']:
            raise ValueError("TRADING_MODE must be 'paper' or 'live'")

        if cls.TRADING_MODE == 'live':
            if not cls.BINANCE_API_KEY or not cls.BINANCE_API_SECRET:
                raise ValueError("API credentials required for live trading")

            print("⚠️  WARNING: LIVE TRADING MODE ENABLED!")
            print("⚠️  Real money will be used. Make sure you know what you're doing!")
            response = input("Type 'I UNDERSTAND THE RISKS' to continue: ")
            if response != "I UNDERSTAND THE RISKS":
                raise ValueError("Live trading cancelled by user")

        if cls.RISK_PER_TRADE > 0.05:
            print(f"⚠️  WARNING: Risk per trade is {cls.RISK_PER_TRADE*100}%")
            print("⚠️  Risking more than 5% per trade is very dangerous!")

        return True
