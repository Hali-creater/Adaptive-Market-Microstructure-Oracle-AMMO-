# modules/data_collector.py

import pandas as pd
import numpy as np
import requests
from utils.helpers import setup_logging

logger = setup_logging()

class DataCollector:
    """
    Collects market data using the Alpha Vantage API.
    """

    def __init__(self, config):
        """
        Initializes the DataCollector with the given configuration.

        Args:
            config: The configuration object containing API keys.
        """
        self.config = config
        self.api_key = self.config.ALPHA_VANTAGE_API_KEY
        self.base_url = "https://www.alphavantage.co/query"
        if not self.config.is_simulation_mode():
            logger.info("DataCollector initialized for Alpha Vantage.")
        else:
            logger.warning("DataCollector is in simulation mode due to missing API keys.")

    def get_price_data(self, symbol: str, time_frame: str, output_size: str = "compact") -> tuple[pd.DataFrame, str | None]:
        """
        Fetches historical stock prices from Alpha Vantage.

        Returns:
            A tuple containing:
                - pd.DataFrame: A DataFrame with historical price data, or an empty DataFrame on error.
                - str | None: An error message string if an error occurred, otherwise None.
        """
        if self.config.is_simulation_mode():
            return self._get_simulated_data(symbol, time_frame)

        # Map our time frames to Alpha Vantage API parameters
        time_frame_map = {
            "Daily": {"function": "TIME_SERIES_DAILY_ADJUSTED", "key": "Time Series (Daily)"},
            "Weekly": {"function": "TIME_SERIES_WEEKLY_ADJUSTED", "key": "Weekly Adjusted Time Series"},
            "Intraday (60min)": {"function": "TIME_SERIES_INTRADAY", "key": "Time Series (60min)", "interval": "60min"},
        }

        if time_frame not in time_frame_map:
            msg = f"Invalid time frame specified: {time_frame}"
            logger.error(msg)
            return pd.DataFrame(), msg

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
            logger.info(f"Fetching {time_frame} data for {symbol} from Alpha Vantage...")
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            data = response.json()

            # Check for specific Alpha Vantage API error messages
            if "Error Message" in data:
                error_msg = f"Alpha Vantage API error for {symbol}: {data['Error Message']}"
                logger.error(error_msg)
                return pd.DataFrame(), error_msg
            if "Information" in data:
                error_msg = f"Alpha Vantage API Information: {data['Information']}. This typically means your API key is invalid or you have exceeded the call frequency limit."
                logger.error(error_msg)
                return pd.DataFrame(), error_msg
            if "Note" in data:
                error_msg = f"Alpha Vantage API Note for {symbol}: {data['Note']}. This might mean you've exceeded the API call frequency. Please wait a minute and try again."
                logger.error(error_msg)
                return pd.DataFrame(), error_msg

            data_key = api_params["key"]
            if data_key not in data:
                error_msg = f"Could not find data key '{data_key}' in the Alpha Vantage response for {symbol}. The symbol may be invalid."
                logger.error(f"{error_msg} Full response: {data}")
                return pd.DataFrame(), error_msg

            df = pd.DataFrame.from_dict(data[data_key], orient="index")

            # Standardize column names
            rename_map = {
                "1. open": "open", "2. high": "high", "3. low": "low", "4. close": "close",
                "5. adjusted close": "adjusted_close", "6. volume": "volume"
            }
            intraday_rename_map = {
                "1. open": "open", "2. high": "high", "3. low": "low", "4. close": "close", "5. volume": "volume"
            }
            df.rename(columns=intraday_rename_map if time_frame == "Intraday (60min)" else rename_map, inplace=True)

            df.index = pd.to_datetime(df.index)
            df = df.astype(float).sort_index()

            logger.info(f"Successfully fetched {len(df)} data points for {symbol}.")
            return df, None

        except requests.exceptions.RequestException as e:
            error_msg = f"A network error occurred while fetching data from Alpha Vantage for {symbol}: {e}"
            logger.error(error_msg)
            return pd.DataFrame(), error_msg
        except (ValueError, KeyError) as e:
            error_msg = f"An error occurred while processing data from Alpha Vantage for {symbol}: {e}"
            logger.error(f"{error_msg}. API Response: {data}")
            return pd.DataFrame(), error_msg

    def _get_simulated_data(self, symbol: str, time_frame: str) -> tuple[pd.DataFrame, str | None]:
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
        return pd.DataFrame(data, index=dates), None