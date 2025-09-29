# utils/constants.py

# --- Constants for the AMMO Trading Agent ---

# Default stock symbol to analyze if none is provided
DEFAULT_SYMBOL = "SPY"

# Timeframes for market data analysis
SUPPORTED_TIMEFRAMES = ["1D", "1W", "1M"]

# Risk management constants
MAX_RISK_PER_TRADE = 0.02  # Max 2% of portfolio per trade
MAX_DRAWDOWN = 0.10      # Max 10% portfolio drawdown

# Sentiment analysis constants
SENTIMENT_POSITIVE_THRESHOLD = 0.6
SENTIMENT_NEUTRAL_THRESHOLD = 0.4
SENTIMENT_NEGATIVE_THRESHOLD = 0.0

# Market personality types
MARKET_PERSONALITIES = {
    "TRENDING_UP": "Trending Up",
    "TRENDING_DOWN": "Trending Down",
    "VOLATILE": "Volatile",
    "RANGE_BOUND": "Range-Bound",
    "NEUTRAL": "Neutral",
}