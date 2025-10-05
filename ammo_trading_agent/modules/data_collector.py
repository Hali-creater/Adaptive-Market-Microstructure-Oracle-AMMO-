# modules/data_collector.py

import pandas as pd
import numpy as np
import finnhub
from datetime import datetime, timedelta
from utils.helpers import setup_logging

logger = setup_logging()

class DataCollector:
    """
    Collects market data using the Finnhub API.
    """

    def __init__(self, config):
        """
        Initializes the DataCollector with the given configuration.

        Args:
            config: The configuration object containing API keys.
        """
        self.config = config
        self.api_key = self.config.FINNHUB_API_KEY
        self.finnhub_client = None
        if not self.config.is_simulation_mode():
            self.finnhub_client = finnhub.Client(api_key=self.api_key)
            logger.info("Finnhub client initialized.")
        else:
            logger.warning("DataCollector is in simulation mode due to missing API keys.")

    def get_price_data(self, symbol: str, time_frame: str, output_size: str = "compact") -> tuple[pd.DataFrame, str | None]:
        """
        Fetches historical stock prices for a given symbol using the Finnhub API.

        Args:
            symbol (str): The stock symbol (e.g., "AAPL").
            time_frame (str): "Daily", "Weekly", or "Intraday (60min)".
            output_size (str): Kept for compatibility, not directly used by Finnhub.

        Returns:
            A tuple containing:
                - pd.DataFrame: A DataFrame with historical price data, or an empty DataFrame on error.
                - str | None: An error message string if an error occurred, otherwise None.
        """
        if self.config.is_simulation_mode() or self.finnhub_client is None:
            df, err = self._get_simulated_data(symbol, time_frame)
            return df, err

        resolution_map = {"Daily": "D", "Weekly": "W", "Intraday (60min)": "60"}
        resolution = resolution_map.get(time_frame)
        if not resolution:
            msg = f"Invalid time frame specified: {time_frame}"
            logger.error(msg)
            return pd.DataFrame(), msg

        to_date = datetime.now()
        from_date = to_date - timedelta(days=30 if time_frame == "Intraday (60min)" else 365)
        from_unix, to_unix = int(from_date.timestamp()), int(to_date.timestamp())

        try:
            logger.info(f"Fetching {time_frame} data for {symbol} from Finnhub...")
            res = self.finnhub_client.stock_candles(symbol, resolution, from_unix, to_unix)

            if res.get('s') != 'ok' or not res.get('c'):
                error_msg = f"Finnhub API returned no data for {symbol}. This could be due to an invalid symbol or an API key with insufficient permissions for this data."
                logger.error(f"Finnhub error for {symbol}: {res}")
                return pd.DataFrame(), error_msg

            df = pd.DataFrame(res)
            df.rename(columns={'o': 'open', 'h': 'high', 'l': 'low', 'c': 'close', 'v': 'volume', 't': 'time'}, inplace=True)
            df['time'] = pd.to_datetime(df['time'], unit='s')
            df.set_index('time', inplace=True)
            df.drop('s', axis=1, inplace=True)

            logger.info(f"Successfully fetched {len(df)} data points for {symbol}.")
            return df.astype(float), None

        except finnhub.FinnhubAPIException as e:
            error_msg = f"Finnhub API error for {symbol}: {e}. Please check if the symbol is correct and your API key is valid."
            logger.error(error_msg)
            return pd.DataFrame(), error_msg
        except Exception as e:
            error_msg = f"An unexpected error occurred while fetching data from Finnhub for {symbol}: {e}"
            logger.error(error_msg)
            return pd.DataFrame(), error_msg

    def _get_simulated_data(self, symbol: str, time_frame: str) -> tuple[pd.DataFrame, str | None]:
        """
        Generates fake market data and matches the return signature of get_price_data.
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
        return pd.DataFrame(data, index=dates), None