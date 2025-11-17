"""
Test script to verify OpenAI integration is working
"""
import os
from dotenv import load_dotenv
from ai_advisor import AITradingAdvisor

# Load environment variables
load_dotenv()

print("="*60)
print("TESTING OPENAI INTEGRATION")
print("="*60)

# Check if API key is set
api_key = os.getenv('OPENAI_API_KEY')
if api_key:
    print(f"✓ OpenAI API key found: {api_key[:20]}...{api_key[-10:]}")
else:
    print("✗ No OpenAI API key found in .env file")
    print("  Please add: OPENAI_API_KEY=sk-your-key-here")
    exit(1)

# Initialize AI advisor
print("\n" + "="*60)
print("Initializing AI Trading Advisor...")
print("="*60)

advisor = AITradingAdvisor()

if not advisor.client:
    print("✗ AI advisor failed to initialize")
    exit(1)

print("✓ AI advisor initialized successfully")

# Test with a sample opportunity
print("\n" + "="*60)
print("Testing AI analysis with sample opportunity...")
print("="*60)

test_opportunity = {
    'symbol': 'BTCUSDT',
    'price': 43500.00,
    'score': 75,
    'direction': 'LONG',
    'rsi': 42.5,
    'macd': 150.23,
    'signal_line': 120.45,
    'volatility': 2.3,
    'volume_24h': 15000000000,
    'signals': ['RSI Oversold', 'MACD Bullish Cross', 'Strong Volume']
}

print(f"\nAnalyzing: {test_opportunity['symbol']}")
print(f"Price: ${test_opportunity['price']:,.2f}")
print(f"Technical Score: {test_opportunity['score']}/100")
print(f"Direction: {test_opportunity['direction']}")
print(f"Signals: {', '.join(test_opportunity['signals'])}")

print("\n⏳ Calling OpenAI GPT-4... (this may take 5-10 seconds)")

try:
    result = advisor.analyze_opportunity(test_opportunity)

    print("\n" + "="*60)
    print("AI ANALYSIS RESULT")
    print("="*60)
    print(f"Should Trade: {'YES ✓' if result['should_trade'] else 'NO ✗'}")
    print(f"Confidence: {result['confidence']*100:.0f}%")
    print(f"Risk Assessment: {result['risk_assessment'].upper()}")
    print(f"\nReasoning:")
    print(result['reasoning'])
    print("="*60)

    print("\n✓ OpenAI integration is WORKING!")
    print("  The bot will use AI to validate trades before executing them.")

except Exception as e:
    print(f"\n✗ AI analysis failed: {e}")
    print("\nPossible issues:")
    print("  1. Invalid API key")
    print("  2. No API credits/quota exceeded")
    print("  3. Network connectivity issue")
    print("  4. OpenAI service issue")
    exit(1)

print("\n" + "="*60)
print("TEST COMPLETE")
print("="*60)
