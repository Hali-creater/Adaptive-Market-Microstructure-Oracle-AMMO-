# modules/sentiment_analyzer.py

import random
import requests
from utils.helpers import setup_logging

logger = setup_logging()

class SentimentAnalyzer:
    """
    Analyzes market sentiment based on news and social media.
    For this example, we'll simulate sentiment analysis.
    """

    def __init__(self, config):
        self.config = config
        self.api_key = self.config.NEWS_API_KEY
        self.base_url = "https://newsapi.org/v2/everything"
        if self.config.is_simulation_mode():
            logger.warning("SentimentAnalyzer is in simulation mode.")

    def get_market_sentiment(self, symbol: str) -> dict:
        """
        Fetches news and performs a mock sentiment analysis.

        Args:
            symbol (str): The stock symbol to analyze.

        Returns:
            dict: A dictionary containing the sentiment score and a summary.
                  Example: {"sentiment_score": 0.7, "summary": "Positive news..."}
        """
        if self.config.is_simulation_mode():
            return self._get_simulated_sentiment(symbol)

        params = {
            "q": symbol,
            "sortBy": "popularity",
            "language": "en",
            "apiKey": self.api_key,
        }
        try:
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            articles = response.json().get("articles", [])

            if not articles:
                return {"sentiment_score": 0.5, "summary": "No recent news found."}

            # In a real scenario, you would use an NLP model here.
            # For now, we just average the "sentiment" of the headlines.
            # This is a very naive approach for demonstration only.
            sentiment_scores = [len(a["title"]) % 10 / 10.0 for a in articles[:10]]
            avg_score = sum(sentiment_scores) / len(sentiment_scores) if sentiment_scores else 0.5

            summary = f"Analyzed {len(articles)} articles. Top headline: '{articles[0]['title']}'"

            return {"sentiment_score": avg_score, "summary": summary}

        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching news for sentiment analysis on {symbol}: {e}")
            return {"sentiment_score": 0.5, "summary": "Error fetching news data."}


    def _get_simulated_sentiment(self, symbol: str) -> dict:
        """
        Generates fake sentiment data for demonstration.
        """
        logger.info(f"Generating simulated sentiment for {symbol}.")
        score = random.uniform(0.1, 0.9)
        sentiments = {
            "Positive": "Overall sentiment is positive, with strong buying signals from social media.",
            "Neutral": "Market sentiment is neutral. Mixed signals from news sources.",
            "Negative": "Negative sentiment detected, driven by recent market news.",
        }
        if score > 0.6:
            summary = sentiments["Positive"]
        elif score > 0.4:
            summary = sentiments["Neutral"]
        else:
            summary = sentiments["Negative"]

        return {"sentiment_score": score, "summary": summary}