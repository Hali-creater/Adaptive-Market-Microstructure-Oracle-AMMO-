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

    def get_price_data(self, symbol: str, time_frame: str, output_size: str = "compact") -> pd.DataFrame:
        """
        Fetches stock prices for a given symbol and time frame.

        Args:
            symbol (str): The stock symbol (e.g., "AAPL").
            time_frame (str): "Daily", "Weekly", or "Intraday (60min)".
            output_size (str): "compact" for last 100 data points, "full" for full history.

        Returns:
            pd.DataFrame: A DataFrame with historical price data, or an empty DataFrame on error.
        """
        if not self.api_key:
            return self._get_simulated_data(symbol, time_frame)

        # Map user-friendly time frame to API parameters
        time_frame_map = {
            "Daily": {"function": "TIME_SERIES_DAILY_ADJUSTED", "key": "Time Series (Daily)"},
            "Weekly": {"function": "TIME_SERIES_WEEKLY_ADJUSTED", "key": "Weekly Adjusted Time Series"},
            "Intraday (60min)": {"function": "TIME_SERIES_INTRADAY", "key": "Time Series (60min)", "interval": "60min"},
        }

        if time_frame not in time_frame_map:
            logger.error(f"Invalid time frame specified: {time_frame}")
            return pd.DataFrame()

        api_params = time_frame_map[time_frame]
        params = {
            "function": api_params["function"],
            "symbol": symbol,
            "outputsize": output_size,
            "apikey": self.api_key,
        }
        if "interval" in api_params:
            params["interval"] = api_params["interval"]

        try:
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            data = response.json()

            data_key = api_params["key"]
            if data_key not in data:
                logger.error(f"Could not fetch {time_frame} data for {symbol}. Response: {data}")
                return pd.DataFrame()

            df = pd.DataFrame.from_dict(data[data_key], orient="index")

            # Standardize column names - they vary slightly across API endpoints
            rename_map = {
                "1. open": "open",
                "2. high": "high",
                "3. low": "low",
                "4. close": "close",
                "5. volume": "volume", # For Intraday
                "6. volume": "volume", # For Daily/Weekly Adjusted
            }
            df.rename(columns=rename_map, inplace=True)

            # Ensure we have a standard set of columns
            standard_columns = ["open", "high", "low", "close", "volume"]
            df = df[[col for col in standard_columns if col in df.columns]]

            df.index = pd.to_datetime(df.index)
            df = df.astype(float).sort_index()
            return df
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching data for {symbol}: {e}")
            return pd.DataFrame()
        except (ValueError, KeyError) as e:
             logger.error(f"Error processing data for {symbol}: {e}. API Response: {data}")
             return pd.DataFrame()

    def _get_simulated_data(self, symbol: str, time_frame: str) -> pd.DataFrame:
        """
        Generates fake market data for demonstration purposes.
        """
        logger.info(f"Generating simulated {time_frame} data for {symbol}.")
        dates = pd.to_datetime(pd.date_range(end=pd.Timestamp.today(), periods=100))
        prices = 100 + np.random.randn(100).cumsum()
        data = {
            "open": prices - np.random.rand(100) * 2,
            "high": prices + np.random.rand(100),
            "low": prices - np.random.rand(100),
            "close": prices,
            "volume": np.random.randint(1_000_000, 10_000_000, size=100),
        }
        df = pd.DataFrame(data, index=dates)
        return df