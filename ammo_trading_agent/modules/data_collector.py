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
            try:
                self.finnhub_client = finnhub.Client(api_key=self.api_key)
                # Test the API key by making a simple call
                self.finnhub_client.company_profile2(symbol='AAPL')
                logger.info("Finnhub client initialized and API key validated successfully.")
            except Exception as e:
                logger.error(f"Failed to initialize Finnhub client or validate API key: {e}. Check if the key is valid.")
                self.finnhub_client = None # Invalidate client if key is bad
        else:
            logger.warning("DataCollector is in simulation mode due to missing API keys.")

    def get_price_data(self, symbol: str, time_frame: str, output_size: str = "compact") -> pd.DataFrame:
        """
        Fetches historical stock prices for a given symbol using the Finnhub API.

        Args:
            symbol (str): The stock symbol (e.g., "AAPL").
            time_frame (str): "Daily", "Weekly", or "Intraday (60min)".
            output_size (str): This argument is kept for compatibility but is not directly used
                               by the Finnhub implementation, which uses date ranges.

        Returns:
            pd.DataFrame: A DataFrame with historical price data, or an empty DataFrame on error.
        """
        if self.config.is_simulation_mode() or self.finnhub_client is None:
            return self._get_simulated_data(symbol, time_frame)

        # Map our time frames to Finnhub's resolutions
        resolution_map = {
            "Daily": "D",
            "Weekly": "W",
            "Intraday (60min)": "60"
        }
        resolution = resolution_map.get(time_frame)
        if not resolution:
            logger.error(f"Invalid time frame specified: {time_frame}")
            return pd.DataFrame()

        # Define date ranges for the API call
        to_date = datetime.now()
        if time_frame == "Intraday (60min)":
            # Fetch last 30 days for intraday
            from_date = to_date - timedelta(days=30)
        else:
            # Fetch last 365 days for daily/weekly
            from_date = to_date - timedelta(days=365)

        from_unix = int(from_date.timestamp())
        to_unix = int(to_date.timestamp())

        try:
            logger.info(f"Fetching {time_frame} data for {symbol} from Finnhub...")
            res = self.finnhub_client.stock_candles(symbol, resolution, from_unix, to_unix)

            if res['s'] != 'ok' or not res.get('c'):
                logger.error(f"Finnhub returned no data or an error for {symbol}: {res}")
                return pd.DataFrame()

            df = pd.DataFrame(res)

            # Rename columns to the standard format used by the application
            df.rename(columns={
                'o': 'open',
                'h': 'high',
                'l': 'low',
                'c': 'close',
                'v': 'volume',
                't': 'time'
            }, inplace=True)

            # Convert Unix timestamp to datetime and set as index
            df['time'] = pd.to_datetime(df['time'], unit='s')
            df.set_index('time', inplace=True)

            # Drop the status column 's'
            df.drop('s', axis=1, inplace=True)

            logger.info(f"Successfully fetched {len(df)} data points for {symbol}.")
            return df.astype(float)

        except Exception as e:
            logger.error(f"An error occurred while fetching data from Finnhub for {symbol}: {e}")
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