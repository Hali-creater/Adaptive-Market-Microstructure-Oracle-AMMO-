# modules/data_collector.py

import pandas as pd
import yfinance as yf
from utils.helpers import setup_logging

logger = setup_logging()

class DataCollector:
    """
    Collects market data using the yfinance library.
    This approach does not require an API key.
    """

    def __init__(self):
        """
        Initializes the DataCollector.
        """
        logger.info("DataCollector initialized to use yfinance.")

    def get_price_data(self, symbol: str, time_frame: str, output_size: str = "compact") -> tuple[pd.DataFrame, str | None]:
        """
        Fetches historical stock prices from Yahoo Finance.

        Args:
            symbol (str): The stock symbol (e.g., "AAPL").
            time_frame (str): "Daily", "Weekly", or "Intraday (60min)".
            output_size (str): This argument is kept for compatibility but is not directly used
                               by the yfinance implementation, which uses date ranges.

        Returns:
            A tuple containing:
                - pd.DataFrame: A DataFrame with historical price data, or an empty DataFrame on error.
                - str | None: An error message string if an error occurred, otherwise None.
        """
        try:
            ticker = yf.Ticker(symbol)

            # Map our time frames to yfinance parameters
            period = "1y" # Default period for daily and weekly
            interval = "1d" # Default interval for daily
            if time_frame == "Weekly":
                interval = "1wk"
            elif time_frame == "Intraday (60min)":
                period = "1mo" # Fetch 1 month of data for intraday
                interval = "60m"

            logger.info(f"Fetching {time_frame} data for {symbol} from yfinance...")
            hist = ticker.history(period=period, interval=interval)

            if hist.empty:
                error_msg = f"No data found for symbol '{symbol}'. It may be an invalid ticker."
                logger.error(error_msg)
                return pd.DataFrame(), error_msg

            # Standardize column names to lowercase
            hist.rename(columns={
                'Open': 'open',
                'High': 'high',
                'Low': 'low',
                'Close': 'close',
                'Volume': 'volume'
            }, inplace=True)

            # Ensure the index is timezone-naive to prevent issues with other modules
            hist.index = hist.index.tz_localize(None)

            logger.info(f"Successfully fetched {len(hist)} data points for {symbol}.")
            return hist, None

        except Exception as e:
            error_msg = f"An unexpected error occurred while fetching data for {symbol} using yfinance: {e}"
            logger.error(error_msg)
            return pd.DataFrame(), error_msg