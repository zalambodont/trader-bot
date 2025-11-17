"""
Technical indicators for trading strategies
"""
import pandas as pd
import numpy as np
from ta.momentum import RSIIndicator
from ta.trend import MACD, EMAIndicator, SMAIndicator
from ta.volatility import BollingerBands


class TechnicalIndicators:
    """Calculate various technical indicators for trading"""

    @staticmethod
    def add_rsi(df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
        """
        Add RSI (Relative Strength Index) to dataframe

        RSI measures momentum - values above 70 indicate overbought (potential sell),
        values below 30 indicate oversold (potential buy)
        """
        rsi = RSIIndicator(close=df['close'], window=period)
        df['rsi'] = rsi.rsi()
        return df

    @staticmethod
    def add_macd(df: pd.DataFrame, fast: int = 12, slow: int = 26, signal: int = 9) -> pd.DataFrame:
        """
        Add MACD (Moving Average Convergence Divergence)

        MACD shows relationship between two moving averages
        - When MACD crosses above signal line: bullish (buy signal)
        - When MACD crosses below signal line: bearish (sell signal)
        """
        macd = MACD(
            close=df['close'],
            window_fast=fast,
            window_slow=slow,
            window_sign=signal
        )
        df['macd'] = macd.macd()
        df['macd_signal'] = macd.macd_signal()
        df['macd_diff'] = macd.macd_diff()
        return df

    @staticmethod
    def add_moving_averages(df: pd.DataFrame, periods: list = [20, 50, 200]) -> pd.DataFrame:
        """
        Add Simple Moving Averages (SMA)

        Moving averages smooth price data to identify trends
        - Price above MA: uptrend
        - Price below MA: downtrend
        - MA crossovers generate trading signals
        """
        for period in periods:
            sma = SMAIndicator(close=df['close'], window=period)
            df[f'sma_{period}'] = sma.sma_indicator()

        return df

    @staticmethod
    def add_ema(df: pd.DataFrame, periods: list = [12, 26]) -> pd.DataFrame:
        """
        Add Exponential Moving Averages (EMA)

        EMA gives more weight to recent prices, more responsive than SMA
        """
        for period in periods:
            ema = EMAIndicator(close=df['close'], window=period)
            df[f'ema_{period}'] = ema.ema_indicator()

        return df

    @staticmethod
    def add_bollinger_bands(df: pd.DataFrame, period: int = 20, std_dev: int = 2) -> pd.DataFrame:
        """
        Add Bollinger Bands

        Bands expand/contract based on volatility
        - Price near upper band: potentially overbought
        - Price near lower band: potentially oversold
        - Bands squeeze: volatility breakout likely
        """
        bb = BollingerBands(close=df['close'], window=period, window_dev=std_dev)
        df['bb_upper'] = bb.bollinger_hband()
        df['bb_middle'] = bb.bollinger_mavg()
        df['bb_lower'] = bb.bollinger_lband()
        df['bb_width'] = bb.bollinger_wband()
        return df

    @staticmethod
    def add_volume_indicators(df: pd.DataFrame) -> pd.DataFrame:
        """
        Add volume-based indicators

        Volume confirms price movements
        - High volume + price increase: strong uptrend
        - High volume + price decrease: strong downtrend
        """
        # Volume moving average
        df['volume_sma'] = df['volume'].rolling(window=20).mean()

        # Volume ratio (current volume vs average)
        df['volume_ratio'] = df['volume'] / df['volume_sma']

        return df

    @staticmethod
    def add_all_indicators(df: pd.DataFrame) -> pd.DataFrame:
        """Add all technical indicators to the dataframe"""
        df = TechnicalIndicators.add_rsi(df)
        df = TechnicalIndicators.add_macd(df)
        df = TechnicalIndicators.add_moving_averages(df)
        df = TechnicalIndicators.add_ema(df)
        df = TechnicalIndicators.add_bollinger_bands(df)
        df = TechnicalIndicators.add_volume_indicators(df)

        return df

    @staticmethod
    def generate_signals(df: pd.DataFrame) -> pd.DataFrame:
        """
        Generate buy/sell signals based on indicators

        Returns: DataFrame with 'signal' column (1=buy, -1=sell, 0=hold)
        """
        df['signal'] = 0

        # RSI signals
        df.loc[df['rsi'] < 30, 'rsi_signal'] = 1  # Oversold - buy
        df.loc[df['rsi'] > 70, 'rsi_signal'] = -1  # Overbought - sell
        df.loc[(df['rsi'] >= 30) & (df['rsi'] <= 70), 'rsi_signal'] = 0

        # MACD signals
        df['macd_signal_line'] = 0
        df.loc[df['macd'] > df['macd_signal'], 'macd_signal_line'] = 1  # Bullish
        df.loc[df['macd'] < df['macd_signal'], 'macd_signal_line'] = -1  # Bearish

        # MACD crossover (change in signal)
        df['macd_cross'] = df['macd_signal_line'].diff()

        # Moving average crossover (Golden Cross / Death Cross)
        if 'sma_50' in df.columns and 'sma_200' in df.columns:
            df['ma_signal'] = 0
            df.loc[df['sma_50'] > df['sma_200'], 'ma_signal'] = 1  # Golden cross - bullish
            df.loc[df['sma_50'] < df['sma_200'], 'ma_signal'] = -1  # Death cross - bearish

        return df
