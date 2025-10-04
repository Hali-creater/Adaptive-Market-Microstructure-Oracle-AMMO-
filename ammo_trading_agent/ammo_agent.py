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

    def __init__(self, config, portfolio_value: float = 100000.0):
        """
        Initializes the agent and its modules.
        """
        logger.info("Initializing AMMO Trading Agent...")
        self._version = 2.0
        self.config = config
        self.data_collector = DataCollector(config=self.config)
        self.sentiment_analyzer = SentimentAnalyzer(config=self.config)
        self.personality_detector = PersonalityDetector()
        self.risk_manager = RiskManager(portfolio_value=portfolio_value)
        self.analysis_results = {}

    def run_analysis(self, symbol: str, time_frame: str):
        """
        Runs a full analysis for a given stock symbol and time frame.

        Args:
            symbol (str): The stock symbol to analyze.
            time_frame (str): The time frame for the analysis (e.g., "Daily", "Weekly").

        Returns:
            dict: A dictionary containing all analysis results.
        """
        logger.info(f"--- Starting {time_frame} Analysis for {symbol} ---")

        # 1. Collect Data
        price_data = self.data_collector.get_price_data(symbol, time_frame, output_size="compact")
        if price_data.empty:
            logger.error(f"Failed to collect data for {symbol} ({time_frame}). Aborting analysis.")
            return {
                "error": f"Could not retrieve {time_frame} price data for {symbol}. The symbol may be invalid or the API may be unavailable."
            }

        latest_price = price_data['close'].iloc[-1]

        # 2. Analyze Sentiment
        sentiment_data = self.sentiment_analyzer.get_market_sentiment(symbol)

        # 3. Detect Market Personality
        market_personality = self.personality_detector.detect_personality(price_data)

        # 4. Synthesize Recommendation (to determine trade direction first)
        recommendation_details = self._synthesize_recommendation(
            sentiment_score=sentiment_data['sentiment_score'],
            market_personality=market_personality
        )

        # 5. Perform Risk Management
        risk_assessment = self._calculate_risk_parameters(
            latest_price,
            recommendation_details['signal']
        )

        self.analysis_results = {
            "symbol": symbol,
            "latest_price": latest_price,
            "price_data": price_data,
            "sentiment": sentiment_data,
            "market_personality": market_personality,
            "risk_assessment": risk_assessment,
            "recommendation": recommendation_details,
        }

        logger.info(f"--- Analysis for {symbol} Complete ---")
        return self.analysis_results

    def _calculate_risk_parameters(self, entry_price: float, signal: str) -> dict:
        """
        Calculates stop-loss, position size, and target price based on the trade signal.
        """
        RISK_FACTOR = 0.05  # 5% risk for stop-loss calculation
        RISK_REWARD_RATIO = 2.0  # 1:2 risk-to-reward ratio

        # Determine stop-loss based on signal
        if "BUY" in signal:
            stop_loss_price = entry_price * (1 - RISK_FACTOR)
        elif "SELL" in signal:
            stop_loss_price = entry_price * (1 + RISK_FACTOR)
        else: # HOLD or other cases
            stop_loss_price = 0

        # Calculate position size
        position_size = self.risk_manager.calculate_position_size(
            entry_price=entry_price,
            stop_loss_price=stop_loss_price
        )

        # Calculate target price
        target_price = self.risk_manager.calculate_target_price(
            entry_price=entry_price,
            stop_loss_price=stop_loss_price,
            risk_reward_ratio=RISK_REWARD_RATIO
        )

        return {
            "position_size": position_size,
            "stop_loss_price": stop_loss_price,
            "target_price": target_price,
            "risk_reward_ratio": f"1:{RISK_REWARD_RATIO}",
            "portfolio_value": self.risk_manager.portfolio_value,
        }


    def _synthesize_recommendation(self, sentiment_score: float, market_personality: str) -> dict:
        """
        A logic engine to generate a detailed trading recommendation.
        """
        logger.info("Synthesizing final recommendation...")

        # Default to no trade
        should_trade = False
        reason = "Conditions are not optimal for a trade at this time. "

        if market_personality == "Trending Up" and sentiment_score > 0.15:
            signal = "BUY"
            should_trade = True
            reason = f"The stock is in a '{market_personality}' pattern and the market sentiment is positive (score: {sentiment_score:.2f}). This alignment suggests a potential buying opportunity."
            if sentiment_score > 0.5:
                signal = "STRONG BUY"
                reason = f"The stock is in a strong '{market_personality}' pattern with very positive market sentiment (score: {sentiment_score:.2f}). This indicates a high-confidence buying opportunity."

        elif market_personality == "Trending Down" and sentiment_score < -0.15:
            signal = "SELL"
            should_trade = True
            reason = f"The stock is in a '{market_personality}' pattern and the market sentiment is negative (score: {sentiment_score:.2f}). This alignment suggests a potential selling or shorting opportunity."
            if sentiment_score < -0.5:
                signal = "STRONG SELL"
                reason = f"The stock is in a strong '{market_personality}' pattern with very negative market sentiment (score: {sentiment_score:.2f}). This indicates a high-confidence selling or shorting opportunity."

        elif market_personality in ["Volatile", "Range-Bound"]:
            signal = "HOLD"
            reason = f"The market personality is '{market_personality}', which suggests a lack of a clear directional trend. It is advisable to wait for a clearer market structure before entering a trade."

        else: # Covers cases like Trending Up with negative sentiment, or vice-versa
            signal = "HOLD"
            reason = f"The market signals are conflicting. The personality is '{market_personality}' but sentiment is neutral or contrary (score: {sentiment_score:.2f}). It's best to stay on the sidelines."

        return {
            "signal": signal,
            "should_trade": should_trade,
            "reason": reason,
        }