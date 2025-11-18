"""
AI Trading Advisor using OpenAI API
Analyzes market opportunities and provides intelligent trading recommendations
"""

import os
import logging
from openai import OpenAI

logger = logging.getLogger(__name__)


class AITradingAdvisor:
    def __init__(self):
        """
        Initialize AI Trading Advisor with OpenAI API
        """
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            logger.warning("No OPENAI_API_KEY found. AI advisor will be disabled.")
            self.client = None
        else:
            self.client = OpenAI(api_key=api_key)
            logger.info("AI Trading Advisor initialized successfully")

    def analyze_opportunity(self, opportunity):
        """
        Analyze a trading opportunity using AI

        Args:
            opportunity: Dict containing opportunity details

        Returns:
            dict: {
                'should_trade': bool,
                'confidence': float (0-1),
                'reasoning': str,
                'risk_assessment': str
            }
        """
        if not self.client:
            # Fallback to basic analysis if AI is disabled
            return {
                'should_trade': opportunity['score'] >= 70,
                'confidence': opportunity['score'] / 100,
                'reasoning': 'Basic technical analysis only (AI disabled)',
                'risk_assessment': 'medium'
            }

        try:
            # Prepare market context
            context = self._prepare_market_context(opportunity)

            # Get AI recommendation
            response = self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {
                        "role": "system",
                        "content": """You are an expert cryptocurrency trading advisor with deep knowledge of technical analysis,
                        market patterns, and risk management. Analyze trading opportunities and provide clear,
                        actionable recommendations. Be conservative and prioritize capital preservation."""
                    },
                    {
                        "role": "user",
                        "content": f"""Analyze this cryptocurrency trading opportunity:

{context}

Provide your assessment in this format:
TRADE: YES/NO
CONFIDENCE: [0-100]%
REASONING: [Your detailed reasoning]
RISK: LOW/MEDIUM/HIGH

Be specific about technical patterns, market conditions, and potential risks."""
                    }
                ],
                temperature=0.3,
                max_tokens=500
            )

            # Parse AI response
            ai_response = response.choices[0].message.content
            return self._parse_ai_response(ai_response, opportunity)

        except Exception as e:
            error_msg = str(e)
            logger.error(f"AI analysis failed: {error_msg}")

            # Provide more specific error messages
            if "API key" in error_msg.lower() or "authentication" in error_msg.lower():
                reasoning = f"Error: Invalid or missing OpenAI API key. Technical score: {opportunity['score']}/100"
            elif "quota" in error_msg.lower() or "rate limit" in error_msg.lower():
                reasoning = f"Error: OpenAI API quota exceeded or rate limited. Technical score: {opportunity['score']}/100"
            elif "timeout" in error_msg.lower():
                reasoning = f"Error: OpenAI API timeout. Technical score: {opportunity['score']}/100"
            else:
                reasoning = f"Error: AI analysis failed ({error_msg[:50]}...). Technical score: {opportunity['score']}/100"

            # Fallback to technical score
            return {
                'should_trade': opportunity['score'] >= 70,
                'confidence': opportunity['score'] / 100,
                'reasoning': reasoning,
                'risk_assessment': 'medium'
            }

    def _prepare_market_context(self, opp):
        """Prepare market context for AI analysis"""

        signals_text = ', '.join(opp.get('signals', [])) if opp.get('signals') else 'No specific signals'

        context = f"""
Symbol: {opp['symbol']}
Current Price: ${opp['price']}
Technical Score: {opp['score']}/100
Direction: {opp.get('direction', 'NEUTRAL')}

Technical Indicators:
- RSI: {opp.get('rsi', 'N/A')}
- MACD: {opp.get('macd', 'N/A')}
- Signal Line: {opp.get('signal_line', 'N/A')}
- Volatility: {opp.get('volatility', 'N/A')}%
- 24h Volume: ${opp.get('volume_24h', 0):,.0f}

Signals Detected:
{signals_text}
"""
        return context

    def _parse_ai_response(self, response_text, opportunity):
        """Parse AI response into structured format"""

        if not response_text or not response_text.strip():
            return {
                'should_trade': False,
                'confidence': opportunity['score'] / 100,
                'reasoning': 'Error: AI returned empty response',
                'risk_assessment': 'medium'
            }

        lines = response_text.strip().split('\n')
        result = {
            'should_trade': False,
            'confidence': opportunity['score'] / 100,
            'reasoning': '',  # Will be filled in below
            'risk_assessment': 'medium'
        }

        reasoning_found = False
        full_response = response_text  # Keep original for fallback

        for line in lines:
            line = line.strip()

            if line.startswith('TRADE:'):
                result['should_trade'] = 'YES' in line.upper()

            elif line.startswith('CONFIDENCE:'):
                try:
                    # Extract number from "CONFIDENCE: 75%"
                    conf_str = line.split(':')[1].strip().replace('%', '')
                    result['confidence'] = float(conf_str) / 100
                except Exception as e:
                    logger.warning(f"Failed to parse confidence: {e}")

            elif line.startswith('RISK:'):
                try:
                    risk = line.split(':')[1].strip().lower()
                    result['risk_assessment'] = risk
                except Exception as e:
                    logger.warning(f"Failed to parse risk: {e}")

            elif line.startswith('REASONING:'):
                try:
                    result['reasoning'] = line.split(':', 1)[1].strip()
                    reasoning_found = True
                except Exception as e:
                    logger.warning(f"Failed to parse reasoning: {e}")

        # If no reasoning was found in expected format, use full response or show error
        if not reasoning_found or not result['reasoning']:
            if len(full_response) > 0:
                result['reasoning'] = f"AI response (unparsed format): {full_response}"
            else:
                result['reasoning'] = "Error: AI provided no reasoning"

        return result

    def batch_analyze_opportunities(self, opportunities, max_analyze=10):
        """
        Analyze multiple opportunities in batch

        Args:
            opportunities: List of opportunity dicts
            max_analyze: Maximum number to analyze with AI (to save API costs)

        Returns:
            dict: {symbol: analysis_result}
        """
        # Sort by score and take top N
        sorted_opps = sorted(opportunities, key=lambda x: x['score'], reverse=True)[:max_analyze]

        results = {}
        for opp in sorted_opps:
            symbol = opp['symbol']
            logger.info(f"AI analyzing: {symbol}")
            results[symbol] = self.analyze_opportunity(opp)

        return results

    def get_portfolio_recommendation(self, portfolio_stats, market_conditions):
        """
        Get AI recommendation for overall portfolio strategy

        Args:
            portfolio_stats: Current portfolio statistics
            market_conditions: Overall market sentiment and conditions

        Returns:
            dict: Portfolio-level recommendations
        """
        if not self.client:
            return {
                'action': 'hold',
                'reasoning': 'AI advisor disabled'
            }

        try:
            response = self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a portfolio management expert. Provide strategic advice on position sizing and risk management."
                    },
                    {
                        "role": "user",
                        "content": f"""Current Portfolio:
- Total Value: ${portfolio_stats.get('total_value', 0):.2f}
- Open Positions: {portfolio_stats.get('positions_count', 0)}
- Unrealized P&L: ${portfolio_stats.get('total_unrealized_pnl', 0):.2f}
- Return: {portfolio_stats.get('total_return', 0):.2f}%

Market Conditions:
{market_conditions}

Should we: INCREASE exposure, DECREASE exposure, or HOLD current positions?
Provide brief reasoning (max 2 sentences)."""
                    }
                ],
                temperature=0.3,
                max_tokens=200
            )

            return {
                'action': 'hold',  # Parse from response
                'reasoning': response.choices[0].message.content
            }

        except Exception as e:
            logger.error(f"Portfolio analysis failed: {e}")
            return {
                'action': 'hold',
                'reasoning': 'Analysis unavailable'
            }
