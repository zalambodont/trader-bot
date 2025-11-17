<div align="center">

# Crypto Trading Bot

### AI-Powered Multi-Pair Cryptocurrency Trading Bot

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Node 16+](https://img.shields.io/badge/node-16+-green.svg)](https://nodejs.org/)
[![React](https://img.shields.io/badge/react-18.0+-61DAFB.svg)](https://reactjs.org/)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

An AI-powered cryptocurrency trading bot with a modern React dashboard for automated multi-pair trading on Binance. Features real-time market scanning, GPT-4 trade analysis, paper trading mode, and comprehensive risk management.

[Features](#features) • [Quick Start](QUICKSTART.md) • [Documentation](#documentation) • [Contributing](CONTRIBUTING.md)

</div>

---

---

## 🚀 NEW USER? START HERE!

**If you're new to this bot or want to get started quickly, please read:**

### **👉 [QUICKSTART.MD - Step-by-Step Setup Guide for Beginners](QUICKSTART.md)**

The quickstart guide includes:
- Complete installation instructions
- How to get API keys (Binance & OpenAI)
- Environment setup for dummies
- Running your first trade
- Troubleshooting common issues

**This README contains detailed technical documentation. For a beginner-friendly guide, use the QUICKSTART above.**

---

## IMPORTANT WARNING

**This bot will NOT make you a billionaire in a short term.** Cryptocurrency trading is extremely risky and volatile. Most traders lose money. This tool is provided for educational purposes. Key facts:

- No AI system can consistently predict market movements
- Past performance does NOT guarantee future results
- You can lose ALL your invested money
- Start with paper trading (simulated trades)
- Never invest more than you can afford to lose completely
- Transaction fees significantly eat into profits

## Features

### Core Trading
- **AI-Powered Trading Advisor** - GPT-4 analyzes trades before execution
- **Multi-Pair Trading** - Scan and trade multiple cryptocurrency pairs simultaneously
- **Multiple Strategies** - RSI+MACD, Moving Average Crossover, Bollinger Bands
- **Paper Trading Mode** - Practice with simulated money (no real funds required)
- **Advanced Risk Management**
  - Automated stop loss and take profit
  - Position sizing based on portfolio allocation
  - Loss cooldown system (prevents immediate re-entry on losing trades)
- **Backtesting Engine** - Test strategies on historical data before going live

### Dashboard Features
- **Pair Search & Analysis** - Search any pair and view technical analysis with live data
- **Market Scanner** - Automatically find top trading opportunities
- **Real-time Charts** - Live price charts with technical indicators
- **Portfolio Tracking** - Monitor positions, P&L, and performance in real-time
- **24-Hour Trade History** - View closed positions from the last 24 hours with detailed metrics
- **Clean Single-Scrollbar UX** - Optimized interface with one main scrollbar for better usability
- **WebSocket Updates** - Instant updates without page refresh
- **RESTful API** - Full programmatic control of the bot

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
# =============================================================================
# API CREDENTIALS
# =============================================================================

# Binance API Credentials (OPTIONAL - only needed for LIVE trading)
# Get these from https://www.binance.com/en/my/settings/api-management
# Leave BLANK for paper trading (recommended for beginners)
BINANCE_API_KEY=
BINANCE_API_SECRET=

# OpenAI API Key (OPTIONAL - for AI trading advisor)
# Get from https://platform.openai.com/api-keys
# Leave BLANK to disable AI analysis (bot will use technical indicators only)
OPENAI_API_KEY=
```

**Note:** All trading settings (capital, positions, stop loss, etc.) are configured through the dashboard when you start trading. You don't need to set them in the .env file.

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

1. No API keys required - works out of the box!
2. Start the bot using one of the methods above
3. Select "Paper" mode in the dashboard when you click "Configure & Trade"
4. Monitor performance and adjust settings through the dashboard
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

2. Update `.env` with your Binance API keys:
   ```env
   BINANCE_API_KEY=your_real_key
   BINANCE_API_SECRET=your_real_secret
   ```

3. Start the dashboard and select "Live" mode when you click "Configure & Trade"

4. Start with SMALL capital amounts ($10-50) in the dashboard settings

5. Monitor constantly in the first hours/days

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

All risk parameters (stop loss %, take profit %, max positions, etc.) are configured through the dashboard in the "Configure & Trade" settings modal. You can adjust them for each trading session without editing any files.

## Performance Tips

1. **Backtest first** - Always backtest on historical data
2. **Start small** - Begin with minimal position sizes
3. **Diversify timeframes** - Test on different intervals (15m, 1h, 4h)
4. **Monitor closely** - Don't set and forget
5. **Adjust for market conditions** - Bull/bear markets need different strategies
6. **Keep learning** - Study winning and losing trades

## Disclaimer

This software is provided "as is" without warranty of any kind. The authors are not responsible for any financial losses incurred through the use of this bot. Cryptocurrency trading carries substantial risk. You are solely responsible for your trading decisions and outcomes.

## Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details on:
- How to report bugs
- How to suggest enhancements
- Development setup
- Code style guidelines
- Pull request process

Please read our [Code of Conduct](CODE_OF_CONDUCT.md) before contributing.

## Security

Security is critical for a trading bot. Please review our [Security Policy](SECURITY.md) for:
- How to report vulnerabilities
- Security best practices
- API key safety
- Known security considerations

**Never commit API keys or secrets to the repository!**

## Documentation

- **[Quick Start Guide](QUICKSTART.md)** - Step-by-step setup for beginners
- **[Contributing Guide](CONTRIBUTING.md)** - How to contribute to the project
- **[Security Policy](SECURITY.md)** - Security guidelines and reporting
- **[Code of Conduct](CODE_OF_CONDUCT.md)** - Community standards
- **[Changelog](CHANGELOG.md)** - Version history and changes

## Support

- **Issues**: Create a [GitHub Issue](../../issues) for bug reports or feature requests
- **Discussions**: Join [GitHub Discussions](../../discussions) for questions and ideas
- **Documentation**: Check the docs linked above for detailed guides

## Roadmap

Future planned features:
- [ ] Multiple exchange support (Coinbase, Kraken, etc.)
- [ ] Advanced charting with TradingView integration
- [ ] Email/SMS notifications for trades
- [ ] Strategy backtesting with historical data visualization
- [ ] Mobile app (React Native)
- [ ] Machine learning price prediction models
- [ ] Telegram bot integration
- [ ] Portfolio rebalancing strategies

## Community

- Star this repository if you find it useful
- Watch for updates and new features
- Fork to create your own version
- Submit pull requests to contribute

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

**DISCLAIMER:** This software is provided for educational purposes only. Trading cryptocurrency involves substantial risk of loss and is not suitable for every investor. The authors and contributors are not responsible for any financial losses incurred through the use of this software. Never invest more than you can afford to lose completely.

## Acknowledgments

- Built with [Python](https://www.python.org/), [React](https://reactjs.org/), and [Flask](https://flask.palletsprojects.com/)
- Market data from [Binance API](https://binance-docs.github.io/apidocs/)
- AI analysis powered by [OpenAI GPT-4](https://openai.com/)
- Technical indicators from [TA-Lib](https://github.com/mrjbq7/ta-lib)

---

<div align="center">

**Remember: The goal is to learn and trade responsibly, not to get rich quick.**

**Protect your capital first, profits second.**

Made with ❤️ by the open-source community

[⬆ Back to Top](#crypto-trading-bot)

</div>
