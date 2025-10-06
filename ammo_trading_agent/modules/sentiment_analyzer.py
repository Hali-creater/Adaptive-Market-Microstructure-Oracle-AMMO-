# modules/sentiment_analyzer.py

import random
from utils.helpers import setup_logging

logger = setup_logging()

class SentimentAnalyzer:
    """
    Analyzes market sentiment based on news and social media.
    This module now runs in a permanent simulation mode as API key input has been removed.
    """

    def __init__(self):
        """
        Initializes the SentimentAnalyzer.
        """
        logger.info("SentimentAnalyzer initialized in simulation mode.")

    def get_market_sentiment(self, symbol: str) -> dict:
        """
        Generates a mock sentiment analysis.

        Args:
            symbol (str): The stock symbol to analyze.

        Returns:
            dict: A dictionary containing the sentiment score and a summary.
        """
        # This module now exclusively returns simulated data.
        return self._get_simulated_sentiment(symbol)

    def _get_simulated_sentiment(self, symbol: str) -> dict:
        """
        Generates fake sentiment data for demonstration.
        """
        logger.info(f"Generating simulated sentiment for {symbol}.")
        score = random.uniform(-0.5, 0.5) # Provide a more neutral-biased score

        summary = "Sentiment analysis is simulated. The agent's recommendation is primarily based on the stock's market personality (price action)."

        return {"sentiment_score": score, "summary": summary}