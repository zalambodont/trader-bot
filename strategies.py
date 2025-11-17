"""
Trading strategies implementation
"""
import pandas as pd
from typing import Tuple, Optional
from indicators import TechnicalIndicators


class TradingStrategy:
    """Base class for trading strategies"""

    def __init__(self, name: str):
        self.name = name

    def analyze(self, df: pd.DataFrame) -> Tuple[str, float]:
        """
        Analyze market data and return trading signal

        Returns:
            Tuple of (action, confidence) where:
            - action: 'BUY', 'SELL', or 'HOLD'
            - confidence: 0.0 to 1.0 indicating signal strength
        """
        raise NotImplementedError("Strategy must implement analyze method")


class RSI_MACD_Strategy(TradingStrategy):
    """
    Combined RSI and MACD strategy

    BUY when:
    - RSI is oversold (< 30) AND
    - MACD crosses above signal line

    SELL when:
    - RSI is overbought (> 70) AND
    - MACD crosses below signal line
    """

    def __init__(self, rsi_period: int = 14, rsi_oversold: int = 30, rsi_overbought: int = 70):
        super().__init__("RSI_MACD")
        self.rsi_period = rsi_period
        self.rsi_oversold = rsi_oversold
        self.rsi_overbought = rsi_overbought

    def analyze(self, df: pd.DataFrame) -> Tuple[str, float]:
        """Analyze using RSI and MACD indicators"""

        # Add indicators if not present
        if 'rsi' not in df.columns:
            df = TechnicalIndicators.add_rsi(df, self.rsi_period)
        if 'macd' not in df.columns:
            df = TechnicalIndicators.add_macd(df)

        # Get latest values
        latest = df.iloc[-1]
        previous = df.iloc[-2]

        rsi = latest['rsi']
        macd = latest['macd']
        macd_signal = latest['macd_signal']
        prev_macd = previous['macd']
        prev_macd_signal = previous['macd_signal']

        # Check for MACD crossover
        macd_bullish_cross = (prev_macd <= prev_macd_signal) and (macd > macd_signal)
        macd_bearish_cross = (prev_macd >= prev_macd_signal) and (macd < macd_signal)

        # BUY signal
        if rsi < self.rsi_oversold and macd_bullish_cross:
            confidence = min(1.0, (self.rsi_oversold - rsi) / self.rsi_oversold)
            return 'BUY', confidence

        # Strong BUY if both are strongly indicating
        elif rsi < self.rsi_oversold and macd > macd_signal:
            confidence = min(0.7, (self.rsi_oversold - rsi) / self.rsi_oversold)
            return 'BUY', confidence

        # SELL signal
        elif rsi > self.rsi_overbought and macd_bearish_cross:
            confidence = min(1.0, (rsi - self.rsi_overbought) / (100 - self.rsi_overbought))
            return 'SELL', confidence

        # Strong SELL if both are strongly indicating
        elif rsi > self.rsi_overbought and macd < macd_signal:
            confidence = min(0.7, (rsi - self.rsi_overbought) / (100 - self.rsi_overbought))
            return 'SELL', confidence

        return 'HOLD', 0.0


class MovingAverageCrossover(TradingStrategy):
    """
    Moving Average Crossover Strategy

    BUY when: Fast MA crosses above Slow MA (Golden Cross)
    SELL when: Fast MA crosses below Slow MA (Death Cross)
    """

    def __init__(self, fast_period: int = 50, slow_period: int = 200):
        super().__init__("MA_Crossover")
        self.fast_period = fast_period
        self.slow_period = slow_period

    def analyze(self, df: pd.DataFrame) -> Tuple[str, float]:
        """Analyze using moving average crossover"""

        # Add MAs if not present
        if f'sma_{self.fast_period}' not in df.columns:
            df = TechnicalIndicators.add_moving_averages(df, [self.fast_period, self.slow_period])

        latest = df.iloc[-1]
        previous = df.iloc[-2]

        fast_ma = latest[f'sma_{self.fast_period}']
        slow_ma = latest[f'sma_{self.slow_period}']
        prev_fast_ma = previous[f'sma_{self.fast_period}']
        prev_slow_ma = previous[f'sma_{self.slow_period}']

        # Check for crossover
        golden_cross = (prev_fast_ma <= prev_slow_ma) and (fast_ma > slow_ma)
        death_cross = (prev_fast_ma >= prev_slow_ma) and (fast_ma < slow_ma)

        if golden_cross:
            # Calculate confidence based on how far apart the MAs are
            spread = abs(fast_ma - slow_ma) / slow_ma
            confidence = min(1.0, spread * 100)
            return 'BUY', confidence

        elif death_cross:
            spread = abs(fast_ma - slow_ma) / slow_ma
            confidence = min(1.0, spread * 100)
            return 'SELL', confidence

        # Maintain position if already trending
        elif fast_ma > slow_ma:
            return 'HOLD', 0.5  # Bullish trend

        elif fast_ma < slow_ma:
            return 'HOLD', 0.5  # Bearish trend

        return 'HOLD', 0.0


class BollingerBandStrategy(TradingStrategy):
    """
    Bollinger Band Mean Reversion Strategy

    BUY when: Price touches or goes below lower band
    SELL when: Price touches or goes above upper band
    """

    def __init__(self, period: int = 20, std_dev: int = 2):
        super().__init__("Bollinger_Bands")
        self.period = period
        self.std_dev = std_dev

    def analyze(self, df: pd.DataFrame) -> Tuple[str, float]:
        """Analyze using Bollinger Bands"""

        # Add Bollinger Bands if not present
        if 'bb_upper' not in df.columns:
            df = TechnicalIndicators.add_bollinger_bands(df, self.period, self.std_dev)

        latest = df.iloc[-1]
        price = latest['close']
        bb_upper = latest['bb_upper']
        bb_lower = latest['bb_lower']
        bb_middle = latest['bb_middle']

        # Calculate position within bands (0 = lower band, 1 = upper band)
        bb_range = bb_upper - bb_lower
        price_position = (price - bb_lower) / bb_range if bb_range > 0 else 0.5

        # BUY when price is near or below lower band
        if price_position < 0.2:
            confidence = 1.0 - (price_position / 0.2)
            return 'BUY', confidence

        # SELL when price is near or above upper band
        elif price_position > 0.8:
            confidence = (price_position - 0.8) / 0.2
            return 'SELL', confidence

        # Mean reversion: if price far from middle, expect return
        elif price > bb_middle and price_position > 0.6:
            confidence = (price_position - 0.6) / 0.4 * 0.5
            return 'HOLD', confidence  # Weak sell signal

        elif price < bb_middle and price_position < 0.4:
            confidence = (0.4 - price_position) / 0.4 * 0.5
            return 'HOLD', confidence  # Weak buy signal

        return 'HOLD', 0.0


class StrategyFactory:
    """Factory to create strategy instances"""

    @staticmethod
    def get_strategy(strategy_name: str, **kwargs) -> TradingStrategy:
        """Get strategy instance by name"""

        strategies = {
            'rsi_macd': RSI_MACD_Strategy,
            'moving_average': MovingAverageCrossover,
            'bollinger': BollingerBandStrategy
        }

        strategy_class = strategies.get(strategy_name.lower())
        if not strategy_class:
            raise ValueError(f"Unknown strategy: {strategy_name}. Available: {list(strategies.keys())}")

        return strategy_class(**kwargs)
