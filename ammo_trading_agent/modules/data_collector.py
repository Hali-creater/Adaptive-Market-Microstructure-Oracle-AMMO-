# modules/data_collector.py

import pandas as pd
from modules.data_source import YahooFinanceSource, InvestingDotComSource
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
        self.sources = {
            "Yahoo Finance": YahooFinanceSource(),
            "investing.com": InvestingDotComSource()
        }
        logger.info("DataCollector initialized with available sources.")

    def get_price_data(self, symbol: str, time_frame: str, source: str, output_size: str = "compact") -> tuple[pd.DataFrame, str | None]:
        """
        Fetches historical stock prices from the selected source.

        Args:
            symbol (str): The stock symbol (e.g., "AAPL").
            time_frame (str): "Daily", "Weekly", or "Intraday (60min)".
            source (str): The data source to use ("Yahoo Finance" or "investing.com").
            output_size (str): This argument is kept for compatibility but is not directly used
                               by the yfinance implementation, which uses date ranges.

        Returns:
            A tuple containing:
                - pd.DataFrame: A DataFrame with historical price data, or an empty DataFrame on error.
                - str | None: An error message string if an error occurred, otherwise None.
        """
        if source in self.sources:
            return self.sources[source].get_price_data(symbol, time_frame, output_size)
        else:
            error_msg = f"Invalid data source: {source}"
            logger.error(error_msg)
            return pd.DataFrame(), error_msg
