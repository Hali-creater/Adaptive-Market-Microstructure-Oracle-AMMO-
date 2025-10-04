# config.py

import os
import streamlit as st
from dotenv import load_dotenv
from utils.helpers import setup_logging

logger = setup_logging()

class Config:
    """
    A centralized configuration class to manage settings and API keys.
    This class defers the loading of secrets until it is instantiated,
    preventing import-time errors in Streamlit Cloud.
    """
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Config, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        # This check ensures that the initialization logic runs only once
        if not hasattr(self, '_initialized'):
            self._initialized = True
            logger.info("Initializing configuration...")

            # --- DIAGNOSTIC LOGGING ---
            if hasattr(st, 'secrets'):
                logger.info("--- DIAGNOSTICS: st.secrets is available ---")
                try:
                    # Log all top-level keys to understand the structure
                    logger.info(f"Available keys in st.secrets: {st.secrets.keys()}")
                except Exception as e:
                    logger.error(f"Error during diagnostic logging of st.secrets: {e}")
                logger.info("--- END DIAGNOSTICS ---")
            else:
                logger.info("--- DIAGNOSTICS: st.secrets is NOT available ---")
            # --- END DIAGNOSTIC LOGGING ---

            # Load .env file for local development
            self._load_dotenv()

            # --- API Keys ---
            self.ALPHA_VANTAGE_API_KEY = self._get_secret("ALPHA_VANTAGE_API_KEY")
            self.NEWS_API_KEY = self._get_secret("NEWS_API_KEY")
            self.ALPACA_API_KEY = self._get_secret("ALPACA_API_KEY")
            self.ALPACA_SECRET_KEY = self._get_secret("ALPACA_SECRET_KEY")
            self.ALPACA_BASE_URL = self._get_secret("ALPACA_BASE_URL") or "https://paper-api.alpaca.markets"

            # --- Application Settings ---
            self.APP_TITLE = "AMMO Trading Agent"

            # Log the operating mode
            if self.is_simulation_mode():
                logger.warning("Application is running in SIMULATION MODE.")
            else:
                logger.info("All API keys are configured. Application is in LIVE MODE.")

    def _load_dotenv(self):
        """Loads environment variables from a .env file if it exists."""
        dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
        if os.path.exists(dotenv_path):
            load_dotenv(dotenv_path)
            logger.info(".env file found and loaded for local development.")

    def _get_secret(self, secret_name: str) -> str:
        """
        Fetches a secret from Streamlit's secrets manager with a fallback to environment variables.
        """
        try:
            # Prefer Streamlit's secrets manager
            if hasattr(st, 'secrets') and secret_name in st.secrets:
                return st.secrets[secret_name]
        except Exception:
            logger.warning(f"Could not access Streamlit secrets for '{secret_name}'. Falling back to environment variables.")

        # Fallback to environment variable
        return os.getenv(secret_name)

    def is_simulation_mode(self) -> bool:
        """
        Checks if the application should run in simulation mode due to missing API keys.
        """
        if not self.ALPHA_VANTAGE_API_KEY or self.ALPHA_VANTAGE_API_KEY == "YOUR_ALPHA_VANTAGE_API_KEY":
            return True
        if not self.NEWS_API_KEY or self.NEWS_API_KEY == "YOUR_NEWS_API_KEY":
            return True
        return False

# The Config class should be instantiated at runtime in the main app,
# not at import time.