"""
Flask API server for trading bot dashboard
"""
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import threading
import time
from datetime import datetime
from binance_client import BinanceClient
from strategies import StrategyFactory
from risk_management import RiskManager
from indicators import TechnicalIndicators
from backtester import Backtester
from config import Config
from market_scanner import MarketScanner
from multi_pair_bot import MultiPairBot
from ai_advisor import AITradingAdvisor

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Global bot state
bot_state = {
    'running': False,
    'client': None,
    'strategy': None,
    'risk_manager': None,
    'positions': [],
    'trades': [],
    'balance': 10000,
    'starting_balance': 10000,
    'current_price': 0,
    'last_signal': {'action': 'HOLD', 'confidence': 0},
    'performance': {},
    'chart_data': []
}

# Multi-pair bot state
multi_pair_state = {
    'bot': None,
    'running': False,
    'thread': None,
    'scanner': None,
    'mode': 'single',  # 'single' or 'multi'
    'ai_advisor': None
}


def initialize_bot():
    """Initialize bot components"""
    if not bot_state['client']:
        bot_state['client'] = BinanceClient(
            api_key=Config.BINANCE_API_KEY if Config.TRADING_MODE == 'live' else None,
            api_secret=Config.BINANCE_API_SECRET if Config.TRADING_MODE == 'live' else None,
            paper_trading=(Config.TRADING_MODE == 'paper')
        )

        bot_state['strategy'] = StrategyFactory.get_strategy(
            Config.STRATEGY,
            rsi_period=Config.RSI_PERIOD,
            rsi_oversold=Config.RSI_OVERSOLD,
            rsi_overbought=Config.RSI_OVERBOUGHT
        )

        bot_state['risk_manager'] = RiskManager(
            max_positions=Config.MAX_POSITIONS,
            risk_per_trade=Config.RISK_PER_TRADE
        )

        bot_state['balance'] = bot_state['client'].get_account_balance()
        bot_state['starting_balance'] = bot_state['balance']


def trading_loop():
    """Main trading loop running in background"""
    while bot_state['running']:
        try:
            # Get market data
            df = bot_state['client'].get_historical_klines(
                symbol=Config.TRADE_SYMBOL,
                interval='15m',
                limit=500
            )

            if df.empty:
                time.sleep(60)
                continue

            # Add indicators
            df = TechnicalIndicators.add_all_indicators(df)

            # Get current price
            current_price = bot_state['client'].get_current_price(Config.TRADE_SYMBOL)
            bot_state['current_price'] = current_price

            # Update balance and positions
            bot_state['balance'] = bot_state['client'].get_account_balance()
            bot_state['positions'] = bot_state['client'].get_open_positions()

            # Get strategy signal
            action, confidence = bot_state['strategy'].analyze(df)
            bot_state['last_signal'] = {'action': action, 'confidence': confidence}

            # Update chart data (last 100 candles)
            chart_data = df.tail(100).reset_index()
            bot_state['chart_data'] = chart_data.to_dict('records')

            # Get performance
            bot_state['performance'] = bot_state['risk_manager'].get_performance_summary()

            # Emit update to connected clients
            socketio.emit('bot_update', get_bot_status())

            # Execute trades based on signal
            if action == 'BUY' and confidence > 0.6:
                if bot_state['risk_manager'].can_open_position(bot_state['positions']):
                    # Open position logic here
                    pass

            # Check positions for exit
            for position in bot_state['positions']:
                should_exit, reason = bot_state['risk_manager'].should_exit_position(
                    position,
                    current_price
                )
                if should_exit:
                    # Close position logic here
                    pass

            time.sleep(60)  # Wait 1 minute

        except Exception as e:
            print(f"Trading loop error: {e}")
            time.sleep(60)


def get_bot_status():
    """Get current bot status"""
    portfolio_value = bot_state['client'].get_portfolio_value(Config.TRADE_SYMBOL) if bot_state['client'] else 0
    total_return = ((portfolio_value - bot_state['starting_balance']) / bot_state['starting_balance'] * 100) if bot_state['starting_balance'] > 0 else 0

    return {
        'running': bot_state['running'],
        'mode': Config.TRADING_MODE,
        'symbol': Config.TRADE_SYMBOL,
        'strategy': Config.STRATEGY,
        'current_price': bot_state['current_price'],
        'balance': bot_state['balance'],
        'portfolio_value': portfolio_value,
        'total_return': total_return,
        'positions': bot_state['positions'],
        'open_positions': len(bot_state['positions']),
        'max_positions': Config.MAX_POSITIONS,
        'last_signal': bot_state['last_signal'],
        'performance': bot_state['performance'],
        'timestamp': datetime.now().isoformat()
    }


# API Routes
@app.route('/api/status', methods=['GET'])
def status():
    """Get bot status"""
    initialize_bot()
    return jsonify(get_bot_status())


@app.route('/api/start', methods=['POST'])
def start_bot():
    """Start trading bot"""
    if bot_state['running']:
        return jsonify({'error': 'Bot already running'}), 400

    initialize_bot()
    bot_state['running'] = True

    # Start trading loop in background thread
    thread = threading.Thread(target=trading_loop, daemon=True)
    thread.start()

    return jsonify({'message': 'Bot started', 'status': get_bot_status()})


@app.route('/api/stop', methods=['POST'])
def stop_bot():
    """Stop trading bot"""
    bot_state['running'] = False
    return jsonify({'message': 'Bot stopped', 'status': get_bot_status()})


@app.route('/api/chart', methods=['GET'])
def get_chart_data():
    """Get chart data for visualization"""
    initialize_bot()

    symbol = request.args.get('symbol', Config.TRADE_SYMBOL)
    interval = request.args.get('interval', '15m')
    limit = int(request.args.get('limit', 100))

    df = bot_state['client'].get_historical_klines(symbol, interval, limit)

    if df.empty:
        return jsonify({'error': 'Failed to fetch data'}), 500

    # Add indicators
    df = TechnicalIndicators.add_all_indicators(df)

    # Convert to JSON-friendly format and replace NaN with None
    df_reset = df.reset_index()
    df_reset['timestamp'] = df_reset['timestamp'].astype(str)

    # Convert to dict and replace NaN with None
    import math
    data_records = df_reset.to_dict('records')
    for record in data_records:
        for key, value in record.items():
            if isinstance(value, float) and math.isnan(value):
                record[key] = None

    return jsonify({
        'data': data_records
    })


@app.route('/api/backtest', methods=['POST'])
def run_backtest():
    """Run backtest on historical data"""
    data = request.json
    strategy_name = data.get('strategy', 'rsi_macd')
    interval = data.get('interval', '1h')
    limit = data.get('limit', 1000)

    initialize_bot()

    # Get historical data
    df = bot_state['client'].get_historical_klines(
        Config.TRADE_SYMBOL,
        interval,
        limit
    )

    if df.empty:
        return jsonify({'error': 'Failed to fetch historical data'}), 500

    # Create strategy
    strategy = StrategyFactory.get_strategy(strategy_name)

    # Run backtest
    backtester = Backtester(strategy, initial_balance=10000)
    results = backtester.run(df, verbose=False)

    return jsonify(results)


@app.route('/api/config', methods=['GET'])
def get_config():
    """Get current configuration"""
    return jsonify({
        'trading_mode': Config.TRADING_MODE,
        'symbol': Config.TRADE_SYMBOL,
        'strategy': Config.STRATEGY,
        'trade_amount': Config.TRADE_AMOUNT_USDT,
        'max_positions': Config.MAX_POSITIONS,
        'risk_per_trade': Config.RISK_PER_TRADE,
        'stop_loss_percent': Config.STOP_LOSS_PERCENT,
        'take_profit_percent': Config.TAKE_PROFIT_PERCENT,
        'rsi_period': Config.RSI_PERIOD,
        'rsi_oversold': Config.RSI_OVERSOLD,
        'rsi_overbought': Config.RSI_OVERBOUGHT
    })


@app.route('/api/positions', methods=['GET'])
def get_positions():
    """Get open positions"""
    initialize_bot()
    return jsonify({
        'positions': bot_state['positions'],
        'count': len(bot_state['positions'])
    })


@app.route('/api/trades', methods=['GET'])
def get_trades():
    """Get trade history"""
    return jsonify({
        'trades': bot_state['trades']
    })


# ===== MULTI-PAIR SCANNER ENDPOINTS =====

@app.route('/api/scanner/scan', methods=['POST'])
def trigger_scan():
    """Trigger a market scan with AI analysis"""
    try:
        data = request.json or {}
        min_score = data.get('min_score', 60)

        if not multi_pair_state['scanner']:
            multi_pair_state['scanner'] = MarketScanner(
                quote_currency='USDT',
                min_volume_usdt=1000000,
                max_pairs=100
            )

        if not multi_pair_state['ai_advisor']:
            multi_pair_state['ai_advisor'] = AITradingAdvisor()

        opportunities = multi_pair_state['scanner'].scan_market(min_score=min_score)

        # Add AI analysis to each opportunity
        for opp in opportunities:
            try:
                ai_analysis = multi_pair_state['ai_advisor'].analyze_opportunity(opp)
                opp['ai_analysis'] = ai_analysis
            except Exception as e:
                print(f"AI analysis failed for {opp['symbol']}: {e}")
                # Continue without AI analysis for this opportunity

        return jsonify({
            'success': True,
            'opportunities': opportunities,
            'count': len(opportunities)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/scanner/opportunities', methods=['GET'])
def get_opportunities():
    """Get current opportunities from scanner with AI analysis"""
    if not multi_pair_state['scanner']:
        return jsonify({'opportunities': [], 'count': 0})

    limit = request.args.get('limit', 20, type=int)
    opportunities = multi_pair_state['scanner'].get_top_opportunities(limit)

    # Add AI analysis if not already present and AI advisor is available
    if multi_pair_state['ai_advisor']:
        for opp in opportunities:
            if 'ai_analysis' not in opp or not opp['ai_analysis']:
                try:
                    ai_analysis = multi_pair_state['ai_advisor'].analyze_opportunity(opp)
                    opp['ai_analysis'] = ai_analysis
                except Exception as e:
                    print(f"AI analysis failed for {opp['symbol']}: {e}")
                    # Continue without AI analysis for this opportunity

    return jsonify({
        'opportunities': opportunities,
        'count': len(opportunities)
    })


@app.route('/api/scanner/status', methods=['GET'])
def get_scanner_status():
    """Get scanner status"""
    if not multi_pair_state['scanner']:
        return jsonify({
            'initialized': False,
            'active_pairs': [],
            'opportunities_count': 0
        })

    return jsonify({
        'initialized': True,
        'active_pairs': multi_pair_state['scanner'].active_pairs,
        'opportunities_count': len(multi_pair_state['scanner'].opportunities),
        'quote_currency': multi_pair_state['scanner'].quote_currency,
        'min_volume': multi_pair_state['scanner'].min_volume_usdt,
        'max_pairs': multi_pair_state['scanner'].max_pairs
    })


@app.route('/api/scanner/analyze-pair', methods=['POST'])
def analyze_pair():
    """Analyze a specific trading pair"""
    try:
        data = request.get_json()
        symbol = data.get('symbol')
        timeframe = data.get('timeframe', '15m')

        if not symbol:
            return jsonify({'success': False, 'error': 'Symbol is required'}), 400

        # Initialize scanner if needed
        if not multi_pair_state['scanner']:
            multi_pair_state['scanner'] = MarketScanner(
                quote_currency='USDT',
                min_volume_usdt=1000000,
                max_pairs=100
            )

        # Initialize AI advisor if needed
        if not multi_pair_state['ai_advisor']:
            multi_pair_state['ai_advisor'] = AITradingAdvisor()

        # Analyze the pair
        opportunity = multi_pair_state['scanner'].analyze_pair(symbol, timeframe)

        if opportunity:
            # Add AI analysis to the opportunity
            try:
                ai_analysis = multi_pair_state['ai_advisor'].analyze_opportunity(opportunity)
                opportunity['ai_analysis'] = ai_analysis
                print(f"✅ AI analysis added for manually searched pair: {symbol}")
            except Exception as e:
                print(f"⚠️ AI analysis failed for {symbol}: {e}")
                # Continue without AI analysis

            return jsonify({
                'success': True,
                'opportunity': opportunity
            })
        else:
            return jsonify({
                'success': False,
                'error': f'Could not analyze {symbol}'
            }), 404

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/pairs', methods=['GET'])
def get_pairs():
    """Get list of all available trading pairs"""
    try:
        if not multi_pair_state['scanner']:
            multi_pair_state['scanner'] = MarketScanner(
                quote_currency='USDT',
                min_volume_usdt=1000000,
                max_pairs=100
            )

        # Get all USDT pairs from Binance
        client = BinanceClient()
        exchange_info = client.client.get_exchange_info()

        # Filter for USDT pairs that are trading
        usdt_pairs = []
        for symbol_info in exchange_info['symbols']:
            if (symbol_info['quoteAsset'] == 'USDT' and
                symbol_info['status'] == 'TRADING'):
                usdt_pairs.append(symbol_info['symbol'])

        # Sort alphabetically
        usdt_pairs.sort()

        return jsonify({
            'success': True,
            'pairs': usdt_pairs,
            'count': len(usdt_pairs)
        })
    except Exception as e:
        # Fallback to common pairs if API fails
        common_pairs = [
            'BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'SOLUSDT', 'ADAUSDT',
            'XRPUSDT', 'DOGEUSDT', 'MATICUSDT', 'DOTUSDT', 'AVAXUSDT',
            'LINKUSDT', 'UNIUSDT', 'ATOMUSDT', 'LTCUSDT', 'NEARUSDT'
        ]
        return jsonify({
            'success': True,
            'pairs': common_pairs,
            'count': len(common_pairs)
        })


@app.route('/api/multi-bot/start', methods=['POST'])
def start_multi_bot():
    """Start multi-pair trading bot"""
    try:
        if multi_pair_state['running']:
            return jsonify({'error': 'Multi-pair bot already running'}), 400

        # Create config from request or use defaults
        data = request.json or {}
        config = {
            'QUOTE_CURRENCY': data.get('quote_currency', 'USDT'),
            'MIN_VOLUME_USDT': data.get('min_volume', 1000000),
            'MAX_PAIRS_TO_SCAN': data.get('max_pairs', 100),
            'INITIAL_BALANCE': data.get('initial_balance', 10000),
            'MAX_POSITIONS': data.get('max_positions', 5),
            'MAX_ALLOCATION_PER_TRADE': data.get('max_allocation', 0.20),
            'SCAN_INTERVAL': data.get('scan_interval', 300),
            'MIN_OPPORTUNITY_SCORE': data.get('min_score', 65),
            'TRADING_MODE': data.get('mode', 'paper'),
            'TIMEFRAME': data.get('timeframe', '15m'),
            'STOP_LOSS_PCT': data.get('stop_loss_pct', 0.02),
            'TAKE_PROFIT_PCT': data.get('take_profit_pct', 0.04),
            'RISK_PER_TRADE': 0.02,
            'selected_pairs': data.get('selected_pairs', [])
        }

        multi_pair_state['bot'] = MultiPairBot(config)
        multi_pair_state['mode'] = 'multi'

        # Run in separate thread
        def run_bot():
            multi_pair_state['bot'].start()

        multi_pair_state['thread'] = threading.Thread(target=run_bot, daemon=True)
        multi_pair_state['thread'].start()
        multi_pair_state['running'] = True

        return jsonify({
            'success': True,
            'message': 'Multi-pair bot started',
            'config': config
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/multi-bot/stop', methods=['POST'])
def stop_multi_bot():
    """Stop multi-pair trading bot"""
    try:
        if not multi_pair_state['running']:
            return jsonify({'error': 'Multi-pair bot not running'}), 400

        if multi_pair_state['bot']:
            multi_pair_state['bot'].stop()

        multi_pair_state['running'] = False
        multi_pair_state['mode'] = 'single'

        return jsonify({
            'success': True,
            'message': 'Multi-pair bot stopped'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/multi-bot/close-position', methods=['POST'])
def close_position():
    """Close an individual position"""
    try:
        if not multi_pair_state['bot']:
            return jsonify({'error': 'Bot not running'}), 400

        data = request.get_json()
        symbol = data.get('symbol')

        if not symbol:
            return jsonify({'error': 'Symbol is required'}), 400

        # Get current price for the symbol
        portfolio = multi_pair_state['bot'].portfolio
        if symbol not in portfolio.positions:
            return jsonify({'error': f'No open position for {symbol}'}), 404

        # Get current price from binance client
        try:
            current_price = multi_pair_state['bot'].binance_client.get_current_price(symbol)
        except Exception as e:
            return jsonify({'error': f'Failed to get current price: {str(e)}'}), 500

        # Close the position
        trade = portfolio.close_position(symbol, current_price, reason='MANUAL_CLOSE')

        if trade:
            return jsonify({
                'success': True,
                'message': f'Position closed for {symbol}',
                'trade': trade
            })
        else:
            return jsonify({'error': f'Failed to close position for {symbol}'}), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/multi-bot/status', methods=['GET'])
def get_multi_bot_status():
    """Get multi-pair bot status"""
    if not multi_pair_state['bot']:
        return jsonify({
            'running': False,
            'mode': multi_pair_state['mode'],
            'portfolio': None,
            'opportunities': []
        })

    status = multi_pair_state['bot'].get_status()
    return jsonify(status)


@app.route('/api/multi-bot/trade-history', methods=['GET'])
def get_trade_history():
    """Get recent trade history (last 24 hours)"""
    try:
        hours = request.args.get('hours', 24, type=int)

        if not multi_pair_state['bot']:
            return jsonify({
                'success': True,
                'trades': [],
                'count': 0
            })

        # Get trade history from portfolio manager
        portfolio = multi_pair_state['bot'].portfolio
        recent_trades = portfolio.get_recent_trade_history(hours=hours)

        return jsonify({
            'success': True,
            'trades': recent_trades,
            'count': len(recent_trades)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/mode', methods=['POST'])
def set_trading_mode():
    """Switch between single-pair and multi-pair mode"""
    data = request.json
    mode = data.get('mode', 'single')

    if mode not in ['single', 'multi']:
        return jsonify({'error': 'Invalid mode. Use "single" or "multi"'}), 400

    multi_pair_state['mode'] = mode

    return jsonify({
        'success': True,
        'mode': mode
    })


# WebSocket events
@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    print('Client connected')
    emit('bot_update', get_bot_status())


@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnect"""
    print('Client disconnected')


if __name__ == '__main__':
    print("Starting API server on http://localhost:5001")
    socketio.run(app, host='0.0.0.0', port=5001, debug=False, allow_unsafe_werkzeug=True)
