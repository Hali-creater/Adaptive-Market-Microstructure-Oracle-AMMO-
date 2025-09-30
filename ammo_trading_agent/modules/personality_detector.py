# modules/personality_detector.py

import pandas as pd
import numpy as np
from ..utils.constants import MARKET_PERSONALITIES
from ..utils.helpers import setup_logging

logger = setup_logging()

class PersonalityDetector:
    """
    Determines the current market personality (e.g., trending, volatile, range-bound).
    """

    def __init__(self):
        logger.info("Personality Detector initialized.")

    def detect_personality(self, price_data: pd.DataFrame) -> str:
        """
        Analyzes price data to determine the market personality.

        This is a simplified example. A real-world implementation would use more
        sophisticated indicators like ADX, Bollinger Bands, etc.

        Args:
            price_data (pd.DataFrame): DataFrame with 'high', 'low', and 'close' columns.

        Returns:
            str: A string describing the market personality.
        """
        if price_data.empty or len(price_data) < 20:
            return MARKET_PERSONALITIES["NEUTRAL"]

        # 1. Trend detection (using a simple moving average slope)
        short_ma = price_data['close'].rolling(window=10).mean()
        long_ma = price_data['close'].rolling(window=30).mean()

        # Calculate slope of the long MA
        slope = (long_ma.iloc[-1] - long_ma.iloc[-10]) / 10 if len(long_ma) > 10 else 0

        # 2. Volatility detection (using standard deviation of returns)
        returns = price_data['close'].pct_change().dropna()
        volatility = returns.std() * np.sqrt(252) # Annualized volatility

        # Logic to decide personality
        if abs(slope) > 0.5:
            if slope > 0:
                return MARKET_PERSONALITIES["TRENDING_UP"]
            else:
                return MARKET_PERSONALITIES["TRENDING_DOWN"]
        elif volatility > 0.3: # High volatility threshold
            return MARKET_PERSONALITIES["VOLATILE"]
        else:
            return MARKET_PERSONALITIES["RANGE_BOUND"]

    def get_simulated_personality(self) -> str:
        """
        Returns a random market personality for demonstration.
        """
        return np.random.choice(list(MARKET_PERSONALITIES.values()))