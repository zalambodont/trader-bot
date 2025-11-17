# Quick Start Guide - For Complete Beginners

Get your AI-powered crypto trading bot running in under 30 minutes, even if you've never coded before!

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Getting API Keys](#getting-api-keys)
3. [Installation](#installation)
4. [Configuration](#configuration)
5. [Running the Bot](#running-the-bot)
6. [Using the Dashboard](#using-the-dashboard)
7. [Troubleshooting](#troubleshooting)

---

## Prerequisites

Before you start, make sure you have:
- A computer (Windows, Mac, or Linux)
- Python 3.8 or higher installed ([Download here](https://www.python.org/downloads/))
- Node.js 14 or higher installed ([Download here](https://nodejs.org/))
- A code editor (optional but helpful - [VS Code](https://code.visualstudio.com/) is recommended)

---

## Getting API Keys

You'll need THREE API keys to use all features. **Don't worry - you can start without any keys using paper trading mode!**

### 🔑 Option 1: Start Without Any Keys (Recommended for Beginners)

**You can skip this section and come back later!** The bot works perfectly in paper trading mode without any API keys.

### 🔑 Option 2: Get OpenAI API Key (For AI Trading Advisor)

The AI advisor uses GPT-4 to validate trades. This is **optional** - the bot works without it.

**Step-by-step:**

1. **Create an OpenAI Account**
   - Go to: https://platform.openai.com/signup
   - Sign up with your email or Google account
   - Verify your email if prompted

2. **Add Payment Method** (Required for API access)
   - Go to: https://platform.openai.com/account/billing/overview
   - Click "Add payment method"
   - Add a credit/debit card
   - OpenAI charges per use (typically $0.01-0.05 per trade analysis)
   - Set a usage limit to control costs (recommended: $5-10/month)

3. **Create API Key**
   - Go to: https://platform.openai.com/api-keys
   - Click "+ Create new secret key"
   - Give it a name like "Crypto Trading Bot"
   - **IMPORTANT:** Copy the key immediately - you can't see it again!
   - It looks like: `sk-proj-abcdefgh1234567890...`
   - Save it in a safe place (we'll use it in Step 4)

4. **Cost Estimate**
   - Each AI analysis costs about $0.01-0.05
   - If you trade 10 times per day, that's ~$0.30/day or ~$9/month
   - You can disable AI at any time by setting `USE_AI=False` in the config

### 🔑 Option 3: Get Binance API Keys (For Live Trading Only)

**⚠️ WARNING: Only do this if you plan to use REAL MONEY for live trading. Not needed for paper trading!**

**Step-by-step:**

1. **Create Binance Account**
   - Go to: https://www.binance.com/en/register
   - Sign up with email
   - Complete identity verification (KYC) - required for trading
   - Enable 2FA (Two-Factor Authentication) for security

2. **Create API Key**
   - Log in to Binance
   - Hover over your profile icon (top right)
   - Click "API Management"
   - Click "Create API"
   - Label it: "Trading Bot"
   - Complete 2FA verification

3. **Configure API Key Security Settings**
   - **VERY IMPORTANT:** After creating the key, click "Edit restrictions"
   - **Enable ONLY these permissions:**
     - ✅ "Enable Reading" - allows bot to read prices
     - ✅ "Enable Spot & Margin Trading" - allows bot to trade
     - ❌ "Enable Withdrawals" - **DISABLE THIS!** (prevents anyone from withdrawing your funds)
   - **IP Access Restriction (Recommended):**
     - Choose "Restrict access to trusted IPs only"
     - Add your home/server IP address
     - Find your IP: https://whatismyipaddress.com/
   - Save changes

4. **Save Your Keys**
   - You'll get two keys:
     - **API Key** - like a username (you can see this anytime)
     - **Secret Key** - like a password (**copy NOW - you can't see it again!**)
   - Save both in a safe place (we'll use them in Step 4)

5. **Test with Small Amount First**
   - When you start live trading, use small amounts
   - Only deposit what you can afford to lose
   - Test thoroughly in paper mode first!

---

## Installation

### Step 1: Download/Clone the Code

```bash
# If you have git installed:
git clone <repository-url>
cd Screening

# OR if you downloaded a ZIP file:
# Unzip it and open Terminal/Command Prompt in that folder
```

### Step 2: Install Backend Dependencies (Python)

```bash
# Create a virtual environment (recommended)
python -m venv venv

# Activate it:
# On Mac/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install required packages
pip install -r requirements.txt
```

**If you get errors:**
- Make sure Python 3.8+ is installed: `python --version`
- Try `python3` instead of `python`
- Try `pip3` instead of `pip`

### Step 3: Install Frontend Dependencies (React)

```bash
# Go to frontend folder
cd frontend

# Install packages (this takes 2-5 minutes)
npm install

# Go back to main folder
cd ..
```

**If you get errors:**
- Make sure Node.js is installed: `node --version`
- Try deleting `frontend/node_modules` folder and running `npm install` again

---

## Configuration

### Step 4: Set Up Environment Variables

This is where you add your API keys (if you have them).

**Option A: Start Without API Keys (Paper Trading)**

```bash
# Copy the example file
cp .env.example .env

# Open .env in a text editor and you'll see:
BINANCE_API_KEY=
BINANCE_API_SECRET=
OPENAI_API_KEY=
LOSS_COOLDOWN_MINUTES=30

# Leave API keys BLANK - the bot works without them for paper trading!
# You'll configure trading mode (paper/live) in the dashboard when you start trading
# LOSS_COOLDOWN_MINUTES prevents re-entry on losing trades (default: 30 minutes)
```

**Option B: Add Your API Keys**

Edit the `.env` file with your keys:

```env
# =============================================================================
# API CREDENTIALS
# =============================================================================

# Binance API Credentials (OPTIONAL - only needed for LIVE trading)
# Get these from https://www.binance.com/en/my/settings/api-management
# Leave BLANK for paper trading (recommended for beginners)
BINANCE_API_KEY=YOUR_BINANCE_API_KEY_HERE
BINANCE_API_SECRET=YOUR_BINANCE_SECRET_KEY_HERE

# OpenAI API Key (OPTIONAL - for AI trading advisor)
# Get from https://platform.openai.com/api-keys
# Leave BLANK to disable AI analysis (bot will use technical indicators only)
OPENAI_API_KEY=sk-proj-your-openai-key-here

# =============================================================================
# ADVANCED TRADING CONFIGURATION (OPTIONAL)
# =============================================================================
# NOTE: Most trading settings (capital, max positions, stop loss, take profit, etc.)
# are configured through the dashboard when you start trading.

# Loss Cooldown (minutes) - Prevents re-entry on losing pairs for this duration
# Default: 30 minutes. Set to 0 to disable cooldown.
# Only applies to losses - profitable trades can re-enter immediately.
LOSS_COOLDOWN_MINUTES=30
```

**Important Notes:**
- **NEVER share your API keys with anyone!**
- **NEVER commit `.env` to GitHub!** (It's in `.gitignore` by default)
- Keep `TRADING_MODE=paper` until you're ready for real trading

### Step 5: Test Your OpenAI Integration (Optional)

If you added an OpenAI API key, test that it works:

```bash
python test_ai.py
```

You should see:
```
✓ OpenAI API key found
✓ AI advisor initialized successfully
✓ OpenAI integration is WORKING!
```

If you see errors, check that:
- Your API key is correct (starts with `sk-proj-`)
- You have billing set up on OpenAI
- You have available credits

---

## Running the Bot

### Option A: Dashboard Mode (Recommended - Visual Interface)

This gives you a beautiful web interface to control the bot.

**Terminal 1 - Start Backend:**
```bash
# Make sure you're in the main folder
python api_server.py

# You should see:
# * Running on http://localhost:5001
# Press CTRL+C to quit
```

**Terminal 2 - Start Frontend:**
```bash
# Open a NEW terminal window
cd frontend
npm start

# Browser will auto-open to http://localhost:3000
```

**What you'll see:**
- Market Scanner - Shows trading opportunities
- Search & Select Pairs - Manually pick coins to trade
- Portfolio Stats - Live P&L and positions
- AI Analysis Logs - See what the AI is thinking

### Option B: CLI Mode (Terminal Only)

Just want to run the bot in the terminal? Use this:

```bash
python multi_pair_bot.py
```

---

## Using the Dashboard

### 1. Scan the Market

1. Set your minimum score (default: 65)
2. Click "Scan Market" to find opportunities
3. Bot analyzes all USDT pairs on Binance
4. Green scores (80+) are strongest opportunities

### 2. Manual Pair Selection

**Want to trade specific coins like DASH or ZEC?**

1. Use the search box at the top
2. Type "DASH" and select from dropdown
3. Selected pairs show as blue chips
4. Click "Configure & Trade" when ready

**⚠️ If search doesn't work:**
- Hard refresh your browser: `Ctrl+Shift+R` (Windows) or `Cmd+Shift+R` (Mac)
- Make sure the backend is running
- Check browser console for errors (F12)

### 3. Start Trading

1. Select pairs you want to trade (or use auto-scan results)
2. Click "Configure & Trade"
3. Set your trading parameters:
   - Total Capital: How much money to use
   - Max Positions: How many trades at once
   - Min Score: Quality threshold (higher = more conservative)
   - Stop Loss %: When to cut losses (e.g., 2%)
   - Take Profit %: When to take profits (e.g., 4%)
   - Trading Mode: **PAPER** or Live (use Paper!)
4. Click "Start Trading"

### 4. Monitor Your Trades

The dashboard shows:
- **Portfolio Value**: Total account value
- **P&L**: Profit/Loss (green = profit, red = loss)
- **Active Positions**: Currently open trades with live P&L
- **24-Hour Trade History**: Closed positions from the last 24 hours (below active positions)
- **AI Analysis**: What the AI thinks about each trade

**💡 Trade History Table shows:**
- Symbol, direction (LONG/SHORT), entry/exit prices
- Profit/Loss for each closed trade
- Close reason (STOP_LOSS, TAKE_PROFIT, etc.)
- Win/loss indicator (green border = win, red = loss)

**🛡️ Loss Cooldown Protection:**
The bot automatically prevents re-entry on pairs that hit stop loss for 30 minutes. This gives the market time to stabilize and prevents revenge trading. Profitable trades can re-enter immediately.

### 5. Backend Console Logs

The backend terminal shows detailed logs with emojis:

```
🔍 SCANNING MARKET (Scan #1)
================================================================================
📋 Scanning 2 MANUALLY SELECTED pairs: DASHUSDT, ZECUSDT
  ✓ DASHUSDT: Score=72, Direction=LONG, Price=$34.50

🤖 AI ANALYZING: DASHUSDT...
   ✅ AI APPROVED: DASHUSDT
      Confidence: 75%, Risk: MEDIUM

💰 EXECUTING TRADE: DASHUSDT
================================================================================
   Direction:    LONG
   Entry Price:  $34.50000000
   Quantity:     5.79710145
   Stop Loss:    $33.81 (-2.0%)
   Take Profit:  $35.88 (+4.0%)
   Tech Score:   72/100
   Signals:      RSI Oversold, Strong Volume

📈 Portfolio: $10000.00 | P&L: $0.00 (0.00%) | Positions: 1/5
```

**What the emojis mean:**
- 🔍 = Market scanning
- 📋 = Manual selection
- 🎯 = Force trading (bypassing AI)
- 🤖 = AI analyzing
- ✅ = AI approved
- ❌ = AI rejected
- 💰 = Trade executing
- 🚪 = Position closing
- 📈 = Profit
- 📉 = Loss
- ➖ = Break even

### 6. Stop Trading

Click "Close All & Take Profit" to:
- Close all open positions
- Realize your P&L
- Stop the bot

---

## Troubleshooting

### "Module not found" Error

```bash
# Make sure you're in the virtual environment
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate     # Windows

# Reinstall packages
pip install -r requirements.txt
```

### React Won't Start

```bash
cd frontend
rm -rf node_modules
npm install
npm start
```

### Search Bar Not Finding Pairs

**This is usually a browser cache issue!**

1. Hard refresh: `Ctrl+Shift+R` (Windows) or `Cmd+Shift+R` (Mac)
2. Clear browser cache completely
3. Try a different browser
4. Make sure backend is running

### "Bot Not Running" Error

Make sure:
1. Backend is running (`python api_server.py`)
2. You clicked "Start Trading" in the dashboard
3. Check backend terminal for errors

### OpenAI "Insufficient Quota" Error

Your OpenAI account needs billing set up:
1. Go to https://platform.openai.com/account/billing
2. Add a payment method
3. Add credits (even $5 works)
4. Set usage limits to control costs

### No Trades Happening

This is usually normal! The bot waits for good opportunities.

**Try:**
- Lower the minimum score (e.g., from 70 to 60)
- Manually select pairs with the search box
- Check that positions aren't already full (max positions reached)
- **Manual selections bypass all checks** - they WILL trade

**Note:** Manual selections force trading regardless of:
- AI approval/rejection
- Technical score
- Momentum or direction

### Trades Taking 20-30 Seconds to Execute

**This is expected!** Here's why:
- Bot scans every 30 seconds (configurable)
- AI analysis takes 5-10 seconds
- Total: 20-35 seconds is normal

---

## Understanding Paper Trading vs Live Trading

### Paper Trading (Fake Money)
- Uses simulated money (default: $10,000)
- No real money at risk
- Reads real market prices from Binance
- **Does NOT require Binance API keys**
- Perfect for learning and testing

### Live Trading (Real Money)
- Uses your real money on Binance
- **Requires Binance API keys**
- All trades are executed on real exchange
- **High risk - only use money you can afford to lose!**

**⚠️ IMPORTANT: Start with paper trading for AT LEAST 1-2 weeks before considering live trading!**

---

## Key Settings Explained

### In `.env` file:

| Setting | What It Does | Required? |
|---------|-------------|-----------|
| `BINANCE_API_KEY` | Your Binance API key | Only for live trading |
| `BINANCE_API_SECRET` | Your Binance secret key | Only for live trading |
| `OPENAI_API_KEY` | Your OpenAI API key | Optional (for AI advisor) |

**Note:** All trading configuration is now done through the dashboard!

### In Dashboard (Configure & Trade):

| Setting | What It Does | Example |
|---------|-------------|---------|
| `Total Capital` | Starting capital | `$10,000` |
| `Max Positions` | Max trades at once | `3` |
| `Min Score` | Quality threshold (0-100) | `65` |
| `Stop Loss %` | Cut losses at this % | `2%` |
| `Take Profit %` | Take profit at this % | `4%` |
| `Scan Interval` | How often to scan (seconds) | `180` (3 min) |
| `Trading Mode` | Paper or live trading | `Paper` |

---

## Advanced Features

### Force Trading Specific Pairs

When you manually select pairs (like DASHUSDT, ZECUSDT):
- They bypass AI approval/rejection
- They bypass technical score requirements
- They force trade as LONG positions
- Useful when you have your own analysis

### AI Trading Advisor

If enabled, GPT-4 analyzes each trade:
- Reviews technical indicators
- Assesses market conditions
- Provides confidence score (0-100%)
- Risk assessment (LOW/MEDIUM/HIGH)
- Can reject trades that look too risky

### Multi-Pair Trading

The bot can trade multiple pairs simultaneously:
- Scans entire Binance USDT market (400+ pairs)
- Finds top opportunities
- Manages up to `MAX_POSITIONS` trades at once
- Diversifies risk across multiple coins

---

## Safety Checklist

Before live trading, make sure:

- [ ] Tested in paper mode for at least 1-2 weeks
- [ ] Understand how the bot makes decisions
- [ ] Set up Binance API with **withdrawals DISABLED**
- [ ] Only using money you can afford to lose
- [ ] Set conservative stop losses (2-3%)
- [ ] Start with SMALL amounts ($100-500)
- [ ] Monitor closely for first few days
- [ ] Have realistic expectations (no get-rich-quick)

---

## What's Next?

### Week 1: Learn
- Run in paper mode
- Watch how it trades
- Check why trades win/lose
- Read about technical indicators (RSI, MACD)

### Week 2: Optimize
- Adjust stop loss/take profit levels
- Try different minimum scores
- Test manual pair selection
- Compare AI on vs off

### Week 3+: Consider Live Trading
- Only if paper trading is profitable
- Start with tiny amounts
- Gradually increase if successful
- Keep learning and improving

---

## Common Questions

**Q: Do I need to pay for anything?**
A: The bot is free. OpenAI API costs $5-10/month if you use AI. Binance has no API fees, only trading fees (0.1%).

**Q: Can I make money with this?**
A: Maybe, but most traders lose money. This is for learning, not guaranteed profits.

**Q: How much should I start with?**
A: Paper trading = $0 (it's fake). Live trading = $100-500 max as a beginner.

**Q: Is this safe?**
A: Paper trading is 100% safe (no real money). Live trading carries high risk.

**Q: Can I run this on my laptop?**
A: Yes! Works on any computer with Python and Node.js.

**Q: Does it work 24/7?**
A: Yes, if you leave it running. Crypto markets never close.

**Q: What if I lose money?**
A: That's part of trading. Never invest more than you can afford to lose.

---

## Need Help?

1. Check the full [README.md](README.md) for detailed documentation
2. Read error messages carefully - they usually tell you what's wrong
3. Check backend terminal for detailed logs
4. Use browser console (F12) to see frontend errors

---

## Legal Disclaimer

This software is provided for educational purposes only. Trading cryptocurrency involves substantial risk of loss. The authors are not responsible for any financial losses incurred. Never trade with money you cannot afford to lose. Past performance does not guarantee future results.

---

**Good luck, trade responsibly, and ALWAYS start with paper trading!** 🚀
