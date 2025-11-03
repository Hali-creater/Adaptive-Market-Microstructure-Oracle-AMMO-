# modules/data_source.py
from abc import ABC, abstractmethod
import pandas as pd
import yfinance as yf
from investiny import historical_data, search_assets
from datetime import datetime, timedelta
from utils.helpers import setup_logging

logger = setup_logging()

class DataSource(ABC):
    @abstractmethod
    def get_price_data(self, symbol: str, time_frame: str, output_size: str = "compact") -> tuple[pd.DataFrame, str | None]:
        """Fetches historical stock prices."""
        pass

class YahooFinanceSource(DataSource):
    def get_price_data(self, symbol: str, time_frame: str, output_size: str = "compact") -> tuple[pd.DataFrame, str | None]:
        try:
            ticker = yf.Ticker(symbol)
            period = "1y"
            interval = "1d"
            if time_frame == "Weekly":
                interval = "1wk"
            elif time_frame == "Intraday (60min)":
                period = "1mo"
                interval = "60m"

            logger.info(f"Fetching {time_frame} data for {symbol} from yfinance...")
            hist = ticker.history(period=period, interval=interval)

            if hist.empty:
                error_msg = f"No data found for symbol '{symbol}'. It may be an invalid ticker."
                logger.error(error_msg)
                return pd.DataFrame(), error_msg

            hist.rename(columns={
                'Open': 'open',
                'High': 'high',
                'Low': 'low',
                'Close': 'close',
                'Volume': 'volume'
            }, inplace=True)
            hist.index = hist.index.tz_localize(None)
            logger.info(f"Successfully fetched {len(hist)} data points for {symbol}.")
            return hist, None
        except Exception as e:
            error_msg = f"An unexpected error occurred while fetching data for {symbol} using yfinance: {e}"
            logger.error(error_msg)
            return pd.DataFrame(), error_msg

class InvestingDotComSource(DataSource):
    def get_price_data(self, symbol: str, time_frame: str, output_size: str = "compact") -> tuple[pd.DataFrame, str | None]:
        try:
            logger.info(f"Searching for {symbol} on investing.com...")
            search_results = search_assets(query=symbol, limit=1)
            if not search_results:
                error_msg = f"Symbol '{symbol}' not found on investing.com."
                logger.error(error_msg)
                return pd.DataFrame(), error_msg

            investing_id = search_results[0]["investing_id"]
            logger.info(f"Found investing_id: {investing_id} for symbol {symbol}")

            to_date = datetime.now()
            if time_frame in ["Daily", "Weekly"]:
                from_date = to_date - timedelta(days=365)
            elif time_frame == "Intraday (60min)":
                from_date = to_date - timedelta(days=30)
            else:
                from_date = to_date - timedelta(days=365)

            from_date_str = from_date.strftime("%d/%m/%Y")
            to_date_str = to_date.strftime("%d/%m/%Y")

            logger.info(f"Fetching {time_frame} data for {symbol} from investing.com...")
            data_dict = historical_data(investing_id=investing_id, from_date=from_date_str, to_date=to_date_str)

            if not data_dict or "historical" not in data_dict:
                error_msg = f"No data found for symbol '{symbol}'. It may be an invalid ticker."
                logger.error(error_msg)
                return pd.DataFrame(), error_msg

            df = pd.DataFrame(data_dict["historical"])
            df.rename(columns={
                'open': 'open',
                'high': 'high',
                'low': 'low',
                'close': 'close',
                'volume': 'volume',
                'date': 'Date'
            }, inplace=True)
            df['Date'] = pd.to_datetime(df['Date'], format='%d/%m/%Y')
            df.set_index('Date', inplace=True)

            logger.info(f"Successfully fetched {len(df)} data points for {symbol}.")
            return df, None
        except Exception as e:
            error_msg = f"An unexpected error occurred while fetching data for {symbol} using investing.com: {e}"
            logger.error(error_msg)
            return pd.DataFrame(), error_msg
