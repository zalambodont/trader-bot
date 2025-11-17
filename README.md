# Crypto Trading Bot

An AI-powered cryptocurrency trading bot with a React dashboard for automated trading on Binance.

## IMPORTANT WARNING

**This bot will NOT make you a billionaire in a short term.** Cryptocurrency trading is extremely risky and volatile. Most traders lose money. This tool is provided for educational purposes. Key facts:

- No AI system can consistently predict market movements
- Past performance does NOT guarantee future results
- You can lose ALL your invested money
- Start with paper trading (simulated trades)
- Never invest more than you can afford to lose completely
- Transaction fees significantly eat into profits

## Features

- Multiple trading strategies (RSI+MACD, Moving Average Crossover, Bollinger Bands)
- Paper trading mode (no real money)
- Risk management (stop loss, take profit, position sizing)
- Backtesting engine to test strategies on historical data
- Real-time React dashboard with live charts
- WebSocket updates for real-time monitoring
- RESTful API for bot control

## Project Structure

```
.
├── binance_client.py      # Binance API wrapper
├── strategies.py          # Trading strategies
├── indicators.py          # Technical indicators
├── risk_management.py     # Risk management system
├── backtester.py          # Backtesting engine
├── trading_bot.py         # Main bot script
├── api_server.py          # Flask API server
├── config.py              # Configuration
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables (create this!)
└── frontend/              # React dashboard
    ├── package.json
    ├── public/
    └── src/
        ├── App.js
        ├── components/
        └── ...
```

## Setup Instructions

### 1. Prerequisites

- Python 3.8 or higher
- Node.js 16 or higher
- Binance account (for live trading only)

### 2. Backend Setup

```bash
# Install Python dependencies
pip install -r requirements.txt

# Create .env file from example
cp .env.example .env

# Edit .env file with your settings
# IMPORTANT: Leave in PAPER mode until you're confident!
nano .env
```

### 3. Configure Environment Variables

Edit `.env` file:

```env
# Binance API (optional for paper trading)
BINANCE_API_KEY=your_key_here
BINANCE_API_SECRET=your_secret_here

# ALWAYS START WITH PAPER TRADING!
TRADING_MODE=paper

# Trading settings
TRADE_SYMBOL=BTCUSDT
TRADE_AMOUNT_USDT=100
MAX_POSITIONS=3
RISK_PER_TRADE=0.02

# Strategy
STRATEGY=rsi_macd
```

### 4. Frontend Setup

```bash
cd frontend
npm install
```

## Running the Bot

### Option 1: CLI Mode (No UI)

Run the trading bot directly:

```bash
python trading_bot.py
```

This will start the bot in the mode specified in your `.env` file.

### Option 2: With Dashboard (Recommended)

**Terminal 1 - Start API Server:**
```bash
python api_server.py
```

**Terminal 2 - Start React Dashboard:**
```bash
cd frontend
npm start
```

Then open your browser to: http://localhost:3000

### Option 3: Run Backtest Only

Test your strategy on historical data without risking any money:

```bash
python run_backtest.py
```

## Usage Guide

### Paper Trading (Recommended First Step)

1. Make sure `.env` has `TRADING_MODE=paper`
2. Start the bot using one of the methods above
3. Monitor performance and adjust settings
4. Run backtests to evaluate strategy effectiveness
5. Only consider live trading after consistent paper trading success

### Live Trading (High Risk!)

**WARNING:** Only proceed if you:
- Have tested extensively in paper mode
- Understand the risks completely
- Can afford to lose ALL invested money
- Have set appropriate risk limits

1. Get Binance API keys from: https://www.binance.com/en/my/settings/api-management
   - Enable "Enable Spot & Margin Trading"
   - Enable "Enable Reading" (required for market data)
   - Add IP whitelist for security
   - **DO NOT** enable withdrawal permissions

2. Update `.env`:
   ```env
   TRADING_MODE=live
   BINANCE_API_KEY=your_real_key
   BINANCE_API_SECRET=your_real_secret
   ```

3. Start with SMALL amounts (`TRADE_AMOUNT_USDT=10` or similar)

4. Monitor constantly in the first hours/days

## Strategies

### RSI + MACD (Default)
- BUY: RSI oversold (<30) AND MACD crosses above signal
- SELL: RSI overbought (>70) AND MACD crosses below signal

### Moving Average Crossover
- BUY: Fast MA crosses above Slow MA (Golden Cross)
- SELL: Fast MA crosses below Slow MA (Death Cross)

### Bollinger Bands
- BUY: Price touches lower band
- SELL: Price touches upper band

## Risk Management

The bot includes built-in risk controls:
- **Stop Loss**: Automatic exit at 2% loss (configurable)
- **Take Profit**: Automatic exit at 5% profit (configurable)
- **Position Sizing**: Limits risk per trade to 2% of capital
- **Max Positions**: Limits concurrent open positions
- **Daily Loss Limit**: Stops trading if daily loss exceeds 5%
- **Max Drawdown**: Stops trading if total drawdown exceeds 20%

## Dashboard Features

- **Real-time price charts** with technical indicators
- **Portfolio statistics** and performance metrics
- **Open positions** with current P&L
- **Trade history** with detailed results
- **Bot controls** (start/stop/backtest)
- **Live updates** via WebSocket

## API Endpoints

- `GET /api/status` - Get bot status
- `POST /api/start` - Start trading bot
- `POST /api/stop` - Stop trading bot
- `GET /api/chart` - Get chart data
- `POST /api/backtest` - Run backtest
- `GET /api/config` - Get configuration
- `GET /api/positions` - Get open positions
- `GET /api/trades` - Get trade history

## Troubleshooting

### Bot won't start
- Check API credentials in `.env`
- Verify internet connection
- Check Binance API status

### No trades executing
- Strategy may not have signals (normal during low volatility)
- Check max positions limit
- Verify sufficient balance

### React dashboard not connecting
- Ensure API server is running on port 5000
- Check CORS settings
- Verify WebSocket connection in browser console

## Customization

### Creating Custom Strategies

Edit `strategies.py` and implement the `TradingStrategy` base class:

```python
class MyStrategy(TradingStrategy):
    def analyze(self, df: pd.DataFrame) -> Tuple[str, float]:
        # Your logic here
        return 'BUY', 0.8  # action, confidence
```

### Adjusting Risk Parameters

Edit `.env` or modify `risk_management.py` directly.

## Performance Tips

1. **Backtest first** - Always backtest on historical data
2. **Start small** - Begin with minimal position sizes
3. **Diversify timeframes** - Test on different intervals (15m, 1h, 4h)
4. **Monitor closely** - Don't set and forget
5. **Adjust for market conditions** - Bull/bear markets need different strategies
6. **Keep learning** - Study winning and losing trades

## Disclaimer

This software is provided "as is" without warranty of any kind. The authors are not responsible for any financial losses incurred through the use of this bot. Cryptocurrency trading carries substantial risk. You are solely responsible for your trading decisions and outcomes.

## License

MIT License - Use at your own risk

## Support

For issues and feature requests, please create an issue in the repository.

---

**Remember: The goal is to learn and trade responsibly, not to get rich quick. Protect your capital first, profits second.**
