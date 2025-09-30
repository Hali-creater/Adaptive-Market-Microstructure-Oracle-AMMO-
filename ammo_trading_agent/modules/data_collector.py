# modules/data_collector.py

import pandas as pd
import numpy as np
import requests
from config import ALPHA_VANTAGE_API_KEY
from utils.helpers import setup_logging

logger = setup_logging()

class DataCollector:
    """
    Collects market data from various sources.
    For this example, we'll use Alpha Vantage.
    """

    def __init__(self, api_key=ALPHA_VANTAGE_API_KEY):
        if not api_key or api_key == "YOUR_ALPHA_VANTAGE_API_KEY":
            logger.warning("Alpha Vantage API key is not set. Data collection will be simulated.")
            self.api_key = None
        else:
            self.api_key = api_key
        self.base_url = "https://www.alphavantage.co/query"

    def get_daily_prices(self, symbol: str, output_size: str = "compact") -> pd.DataFrame:
        """
        Fetches daily stock prices for a given symbol.

        Args:
            symbol (str): The stock symbol (e.g., "AAPL").
            output_size (str): "compact" for last 100 days, "full" for full history.

        Returns:
            pd.DataFrame: A DataFrame with historical price data, or an empty DataFrame on error.
        """
        if not self.api_key:
            return self._get_simulated_data(symbol)

        params = {
            "function": "TIME_SERIES_DAILY_ADJUSTED",
            "symbol": symbol,
            "outputsize": output_size,
            "apikey": self.api_key,
        }
        try:
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            data = response.json()

            if "Time Series (Daily)" not in data:
                logger.error(f"Could not fetch data for {symbol}. Response: {data}")
                return pd.DataFrame()

            df = pd.DataFrame.from_dict(data["Time Series (Daily)"], orient="index")
            df = df.rename(columns={
                "1. open": "open",
                "2. high": "high",
                "3. low": "low",
                "4. close": "close",
                "5. adjusted close": "adjusted_close",
                "6. volume": "volume",
            })
            df.index = pd.to_datetime(df.index)
            df = df.astype(float).sort_index()
            return df
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching data for {symbol}: {e}")
            return pd.DataFrame()

    def _get_simulated_data(self, symbol: str) -> pd.DataFrame:
        """
        Generates fake market data for demonstration purposes.
        """
        logger.info(f"Generating simulated data for {symbol}.")
        dates = pd.to_datetime(pd.date_range(end=pd.Timestamp.today(), periods=100))
        prices = 100 + np.random.randn(100).cumsum()
        data = {
            "open": prices - np.random.rand(100) * 2,
            "high": prices + np.random.rand(100),
            "low": prices - np.random.rand(100),
            "close": prices,
            "adjusted_close": prices * 0.99,
            "volume": np.random.randint(1_000_000, 10_000_000, size=100),
        }
        df = pd.DataFrame(data, index=dates)
        return df