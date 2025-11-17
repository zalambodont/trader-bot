"""
Simple script to run a backtest
"""
from binance_client import BinanceClient
from strategies import StrategyFactory
from backtester import Backtester
from config import Config

def main():
    print("="*60)
    print("CRYPTO TRADING BOT - BACKTEST MODE")
    print("="*60)

    # Initialize client (using public API, no credentials needed)
    print("\nConnecting to Binance...")
    client = BinanceClient(paper_trading=True)

    # Get historical data
    print(f"Fetching historical data for {Config.TRADE_SYMBOL}...")
    df = client.get_historical_klines(
        symbol=Config.TRADE_SYMBOL,
        interval='1h',  # 1 hour candles
        limit=1000      # Last 1000 candles (~42 days)
    )

    if df.empty:
        print("❌ Failed to fetch data. Check your internet connection.")
        return

    print(f"✓ Loaded {len(df)} candles")
    print(f"  Period: {df.index[0]} to {df.index[-1]}")

    # Create strategy
    print(f"\nStrategy: {Config.STRATEGY}")
    strategy = StrategyFactory.get_strategy(
        Config.STRATEGY,
        rsi_period=Config.RSI_PERIOD,
        rsi_oversold=Config.RSI_OVERSOLD,
        rsi_overbought=Config.RSI_OVERBOUGHT
    )

    # Run backtest
    print("\nRunning backtest...")
    print("-"*60)

    backtester = Backtester(
        strategy=strategy,
        initial_balance=10000,
        commission=0.001  # 0.1% fee
    )

    results = backtester.run(df, verbose=True)

    # Additional insights
    if results['total_trades'] > 0:
        print("\n" + "="*60)
        print("INSIGHTS")
        print("="*60)

        if results['total_return'] < 0:
            print("⚠️  Strategy lost money over this period")
            print("   Consider:")
            print("   - Adjusting strategy parameters")
            print("   - Testing a different strategy")
            print("   - Using a different timeframe")
        elif results['total_return'] < 5:
            print("⚠️  Strategy had minimal returns")
            print("   Better to just hold (buy and hold) in this case")
        else:
            print("✓  Strategy showed positive returns")
            print("   But remember: past performance ≠ future results")

        if results['win_rate'] < 40:
            print("\n⚠️  Win rate is low (<40%)")
            print("   Strategy needs improvement")
        elif results['win_rate'] > 60:
            print("\n✓  Win rate is good (>60%)")

        if results['max_drawdown'] < -15:
            print(f"\n⚠️  High drawdown ({results['max_drawdown']:.1f}%)")
            print("   You need strong risk tolerance for this strategy")

        print("\n" + "="*60)
        print("NEXT STEPS")
        print("="*60)
        print("1. Try different strategies (moving_average, bollinger)")
        print("2. Adjust parameters in .env file")
        print("3. Test on different timeframes (5m, 15m, 1h, 4h, 1d)")
        print("4. Once satisfied, try paper trading with: python trading_bot.py")
        print("5. NEVER use live trading until confident with paper trading")
        print("="*60 + "\n")

if __name__ == '__main__':
    main()
