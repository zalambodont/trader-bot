"""
Market Scanner - Scans entire crypto ecosystem for trading opportunities
"""
import time
import pandas as pd
import numpy as np
from binance_client import BinanceClient
from indicators import TechnicalIndicators
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MarketScanner:
    """Scans all trading pairs for opportunities"""

    def __init__(self, quote_currency='USDT', min_volume_usdt=100000, max_pairs=100):
        """
        Initialize scanner

        Args:
            quote_currency: Base quote currency (USDT, BTC, ETH, etc.)
            min_volume_usdt: Minimum 24h volume in USDT to consider
            max_pairs: Maximum number of pairs to monitor
        """
        self.client = BinanceClient()
        self.quote_currency = quote_currency
        self.min_volume_usdt = min_volume_usdt
        self.max_pairs = max_pairs
        self.active_pairs = []
        self.opportunities = []

    def get_all_pairs(self):
        """Fetch all available trading pairs from Binance"""
        try:
            exchange_info = self.client.client.get_exchange_info()
            all_pairs = []

            for symbol_info in exchange_info['symbols']:
                if symbol_info['status'] == 'TRADING' and symbol_info['quoteAsset'] == self.quote_currency:
                    all_pairs.append({
                        'symbol': symbol_info['symbol'],
                        'baseAsset': symbol_info['baseAsset'],
                        'quoteAsset': symbol_info['quoteAsset']
                    })

            logger.info(f"Found {len(all_pairs)} trading pairs with {self.quote_currency}")
            return all_pairs

        except Exception as e:
            logger.error(f"Error fetching pairs: {e}")
            return []

    def filter_by_volume(self, pairs):
        """Filter pairs by 24h trading volume"""
        try:
            ticker_24h = self.client.client.get_ticker()
            volume_data = {t['symbol']: float(t['quoteVolume']) for t in ticker_24h}

            filtered = []
            for pair in pairs:
                symbol = pair['symbol']
                volume = volume_data.get(symbol, 0)

                if volume >= self.min_volume_usdt:
                    pair['volume_24h'] = volume
                    filtered.append(pair)

            # Sort by volume and take top pairs
            filtered.sort(key=lambda x: x['volume_24h'], reverse=True)
            filtered = filtered[:self.max_pairs]

            logger.info(f"Filtered to {len(filtered)} pairs with volume > {self.min_volume_usdt}")
            return filtered

        except Exception as e:
            logger.error(f"Error filtering by volume: {e}")
            return pairs[:self.max_pairs]

    def analyze_pair(self, symbol, timeframe='15m'):
        """
        Analyze a single pair for trading opportunities

        Returns:
            dict with opportunity score and details
        """
        try:
            # Get historical data
            df = self.client.get_historical_klines(symbol, timeframe, limit=100)

            if df.empty or len(df) < 50:
                return None

            # Calculate indicators
            df = TechnicalIndicators.add_rsi(df)
            df = TechnicalIndicators.add_macd(df)
            df = TechnicalIndicators.add_bollinger_bands(df)

            # Get latest values
            latest = df.iloc[-1]
            current_price = latest['close']
            rsi = latest['rsi']
            macd = latest['macd']
            signal = latest['macd_signal']
            bb_upper = latest['bb_upper']
            bb_lower = latest['bb_lower']
            bb_middle = latest['bb_middle']

            # Calculate opportunity score (0-100)
            score = 0
            signals = []

            # RSI signals (more granular)
            if rsi < 25:
                score += 35
                signals.append(f"RSI very oversold ({rsi:.1f})")
            elif rsi < 35:
                score += 25
                signals.append(f"RSI oversold ({rsi:.1f})")
            elif rsi < 40:
                score += 15
                signals.append(f"RSI low ({rsi:.1f})")
            elif rsi > 75:
                score += 35
                signals.append(f"RSI very overbought ({rsi:.1f})")
            elif rsi > 65:
                score += 25
                signals.append(f"RSI overbought ({rsi:.1f})")
            elif rsi > 60:
                score += 15
                signals.append(f"RSI high ({rsi:.1f})")
            elif 45 < rsi < 55:
                score += 5  # Neutral zone

            # MACD signals
            macd_diff = macd - signal
            prev_macd_diff = df.iloc[-2]['macd'] - df.iloc[-2]['macd_signal']

            if macd > signal and prev_macd_diff <= 0:
                score += 40
                signals.append("MACD bullish cross")
            elif macd < signal and prev_macd_diff >= 0:
                score += 40
                signals.append("MACD bearish cross")
            elif macd > signal and macd_diff > prev_macd_diff:
                score += 20
                signals.append("MACD bullish divergence")
            elif macd < signal and macd_diff < prev_macd_diff:
                score += 20
                signals.append("MACD bearish divergence")

            # Bollinger Bands signals (more sensitive)
            bb_position = (current_price - bb_lower) / (bb_upper - bb_lower)
            if bb_position <= 0.1:
                score += 25
                signals.append("Price at lower BB")
            elif bb_position <= 0.2:
                score += 15
                signals.append("Price near lower BB")
            elif bb_position >= 0.9:
                score += 25
                signals.append("Price at upper BB")
            elif bb_position >= 0.8:
                score += 15
                signals.append("Price near upper BB")

            # Price momentum (last 5 candles)
            recent_close = df['close'].iloc[-5:].values
            price_change_pct = ((recent_close[-1] - recent_close[0]) / recent_close[0]) * 100

            if abs(price_change_pct) > 3:
                score += 20
                direction_str = "up" if price_change_pct > 0 else "down"
                signals.append(f"Strong momentum {direction_str} ({abs(price_change_pct):.1f}%)")
            elif abs(price_change_pct) > 1.5:
                score += 10
                direction_str = "up" if price_change_pct > 0 else "down"
                signals.append(f"Momentum {direction_str} ({abs(price_change_pct):.1f}%)")

            # Volume analysis
            avg_volume = df['volume'].iloc[-20:].mean()
            current_volume = df['volume'].iloc[-1]
            volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1

            if volume_ratio > 2:
                score += 20
                signals.append(f"High volume ({volume_ratio:.1f}x avg)")
            elif volume_ratio > 1.5:
                score += 10
                signals.append(f"Increased volume ({volume_ratio:.1f}x avg)")

            # Trend strength (volatility)
            volatility = (bb_upper - bb_lower) / bb_middle * 100
            if volatility > 6:
                score += 15
                signals.append(f"Very high volatility ({volatility:.1f}%)")
            elif volatility > 4:
                score += 10
                signals.append(f"High volatility ({volatility:.1f}%)")
            elif volatility > 2:
                score += 5
                signals.append(f"Moderate volatility ({volatility:.1f}%)")

            # Determine direction (more sensitive)
            direction = None
            bullish_signals = 0
            bearish_signals = 0

            # Count bullish signals
            if rsi < 40:
                bullish_signals += 1
            if macd > signal:
                bullish_signals += 1
            if bb_position < 0.3:
                bullish_signals += 1
            if price_change_pct > 1:
                bullish_signals += 1

            # Count bearish signals
            if rsi > 60:
                bearish_signals += 1
            if macd < signal:
                bearish_signals += 1
            if bb_position > 0.7:
                bearish_signals += 1
            if price_change_pct < -1:
                bearish_signals += 1

            # Determine direction based on signal count (less strict)
            if bullish_signals > bearish_signals:
                direction = 'LONG'
            elif bearish_signals > bullish_signals:
                direction = 'SHORT'
            else:
                # If tied, use momentum as tiebreaker
                if price_change_pct > 0.5:
                    direction = 'LONG'
                elif price_change_pct < -0.5:
                    direction = 'SHORT'

            return {
                'symbol': symbol,
                'score': min(score, 100),
                'price': current_price,
                'rsi': rsi,
                'macd': macd,
                'signal_line': signal,
                'volatility': volatility,
                'direction': direction,
                'signals': signals,
                'timestamp': time.time()
            }

        except Exception as e:
            logger.warning(f"Error analyzing {symbol}: {e}")
            return None

    def scan_market(self, timeframe='15m', min_score=50):
        """
        Scan entire market for opportunities

        Args:
            timeframe: Candlestick timeframe
            min_score: Minimum opportunity score to include

        Returns:
            List of opportunities sorted by score
        """
        logger.info("Starting market scan...")

        # Get and filter pairs
        all_pairs = self.get_all_pairs()
        if not all_pairs:
            return []

        filtered_pairs = self.filter_by_volume(all_pairs)
        self.active_pairs = [p['symbol'] for p in filtered_pairs]

        logger.info(f"Analyzing {len(filtered_pairs)} pairs...")

        # Analyze pairs in parallel
        opportunities = []
        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = {
                executor.submit(self.analyze_pair, pair['symbol'], timeframe): pair
                for pair in filtered_pairs
            }

            for future in as_completed(futures):
                result = future.result()
                if result and result['score'] >= min_score:
                    # Add volume info
                    pair = futures[future]
                    result['volume_24h'] = pair.get('volume_24h', 0)
                    opportunities.append(result)

        # Sort by score
        opportunities.sort(key=lambda x: x['score'], reverse=True)

        self.opportunities = opportunities
        logger.info(f"Found {len(opportunities)} opportunities with score >= {min_score}")

        return opportunities

    def get_top_opportunities(self, n=10):
        """Get top N opportunities"""
        return self.opportunities[:n]

    def get_opportunity_by_symbol(self, symbol):
        """Get opportunity details for specific symbol"""
        for opp in self.opportunities:
            if opp['symbol'] == symbol:
                return opp
        return None

    def continuous_scan(self, interval=300, min_score=50):
        """
        Continuously scan market at intervals

        Args:
            interval: Seconds between scans
            min_score: Minimum score threshold
        """
        logger.info(f"Starting continuous scan (interval: {interval}s)")

        while True:
            try:
                self.scan_market(min_score=min_score)

                if self.opportunities:
                    logger.info(f"Top opportunity: {self.opportunities[0]['symbol']} "
                              f"(score: {self.opportunities[0]['score']}, "
                              f"direction: {self.opportunities[0]['direction']})")

                time.sleep(interval)

            except KeyboardInterrupt:
                logger.info("Scan stopped by user")
                break
            except Exception as e:
                logger.error(f"Error in continuous scan: {e}")
                time.sleep(60)


if __name__ == '__main__':
    # Test the scanner
    scanner = MarketScanner(
        quote_currency='USDT',
        min_volume_usdt=1000000,  # 1M USDT minimum volume
        max_pairs=50
    )

    opportunities = scanner.scan_market(min_score=60)

    print("\n" + "="*80)
    print("TOP TRADING OPPORTUNITIES")
    print("="*80)

    for i, opp in enumerate(opportunities[:10], 1):
        print(f"\n{i}. {opp['symbol']}")
        print(f"   Score: {opp['score']}/100")
        print(f"   Direction: {opp['direction']}")
        print(f"   Price: ${opp['price']:.8f}")
        print(f"   RSI: {opp['rsi']:.1f}")
        print(f"   Volume 24h: ${opp['volume_24h']:,.0f}")
        print(f"   Signals: {', '.join(opp['signals'])}")
