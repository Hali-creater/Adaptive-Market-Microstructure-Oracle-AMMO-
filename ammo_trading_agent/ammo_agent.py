# ammo_agent.py

from modules import DataCollector, SentimentAnalyzer, PersonalityDetector, RiskManager
from utils.helpers import setup_logging

logger = setup_logging()

class AmmoAgent:
    """
    The core logic of the AMMO Trading Agent.
    This class integrates all the modules to provide a comprehensive market analysis
    and a final trading recommendation.
    """

    def __init__(self, portfolio_value: float = 100000.0):
        """
        Initializes the agent and its modules.
        """
        logger.info("Initializing AMMO Trading Agent...")
        self.data_collector = DataCollector()
        self.sentiment_analyzer = SentimentAnalyzer()
        self.personality_detector = PersonalityDetector()
        self.risk_manager = RiskManager(portfolio_value=portfolio_value)
        self.analysis_results = {}

    def run_analysis(self, symbol: str):
        """
        Runs a full analysis for a given stock symbol.

        Args:
            symbol (str): The stock symbol to analyze.

        Returns:
            dict: A dictionary containing all analysis results.
        """
        logger.info(f"--- Starting Analysis for {symbol} ---")

        # 1. Collect Data
        price_data = self.data_collector.get_daily_prices(symbol, output_size="compact")
        if price_data.empty:
            logger.error(f"Failed to collect data for {symbol}. Aborting analysis.")
            return {
                "error": f"Could not retrieve price data for {symbol}. The symbol may be invalid or the API may be unavailable."
            }

        latest_price = price_data['close'].iloc[-1]

        # 2. Analyze Sentiment
        sentiment_data = self.sentiment_analyzer.get_market_sentiment(symbol)

        # 3. Detect Market Personality
        market_personality = self.personality_detector.detect_personality(price_data)

        # 4. Perform Risk Management (example)
        # For a buy signal, let's assume a simple stop-loss 5% below the current price
        stop_loss_price = latest_price * 0.95
        position_size = self.risk_manager.calculate_position_size(
            entry_price=latest_price,
            stop_loss_price=stop_loss_price
        )

        # 5. Synthesize Recommendation (Simple Logic)
        recommendation = self._synthesize_recommendation(
            sentiment_score=sentiment_data['sentiment_score'],
            market_personality=market_personality
        )

        self.analysis_results = {
            "symbol": symbol,
            "latest_price": latest_price,
            "price_data": price_data,
            "sentiment": sentiment_data,
            "market_personality": market_personality,
            "risk_assessment": {
                "position_size": position_size,
                "stop_loss_price": stop_loss_price,
                "portfolio_value": self.risk_manager.portfolio_value,
            },
            "recommendation": recommendation,
        }

        logger.info(f"--- Analysis for {symbol} Complete ---")
        return self.analysis_results

    def _synthesize_recommendation(self, sentiment_score: float, market_personality: str) -> str:
        """
        A simple logic engine to generate a trading recommendation.
        This should be replaced with a more sophisticated strategy.
        """
        logger.info("Synthesizing final recommendation...")

        if market_personality == "Trending Up" and sentiment_score > 0.6:
            return "STRONG BUY"
        elif market_personality == "Trending Up" and sentiment_score > 0.4:
            return "BUY"
        elif market_personality == "Trending Down" and sentiment_score < 0.4:
            return "STRONG SELL"
        elif market_personality == "Trending Down" and sentiment_score < 0.6:
            return "SELL"
        elif market_personality in ["Volatile", "Range-Bound"]:
            return "HOLD - Market is uncertain."
        else:
            return "HOLD"