# config.py

import os
import streamlit as st
from dotenv import load_dotenv
from utils.helpers import setup_logging

logger = setup_logging()

# --- Load Environment Variables ---

# Load from .env file if it exists (for local development)
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
    logger.info(".env file found and loaded.")

# --- API Key Management ---

def get_secret(secret_name: str, fallback_env_var: str) -> str:
    """
    Fetches a secret from Streamlit's secrets manager with a fallback to environment variables.
    Gracefully handles cases where secrets are not configured.
    """
    try:
        # The 'in' operator on st.secrets can raise an error if the secrets file doesn't exist.
        if hasattr(st, 'secrets') and secret_name in st.secrets:
            return st.secrets[secret_name]
    except Exception:
        # If st.secrets is not configured, it can raise an exception.
        # We'll ignore it and fall back to env vars.
        logger.info("Could not access Streamlit secrets. Falling back to .env or environment variables.")
        pass

    # Fallback to environment variable
    return os.getenv(fallback_env_var)

# API Keys from Streamlit secrets or .env file
ALPHA_VANTAGE_API_KEY = get_secret("ALPHA_VANTAGE_API_KEY", "ALPHA_VANTAGE_API_KEY")
NEWS_API_KEY = get_secret("NEWS_API_KEY", "NEWS_API_KEY")
ALPACA_API_KEY = get_secret("ALPACA_API_KEY", "ALPACA_API_KEY")
ALPACA_SECRET_KEY = get_secret("ALPACA_SECRET_KEY", "ALPACA_SECRET_KEY")
ALPACA_BASE_URL = get_secret("ALPACA_BASE_URL", "ALPACA_BASE_URL") or "https://paper-api.alpaca.markets"

# --- Application Settings ---
APP_TITLE = "AMMO Trading Agent"

# --- Mode Validation ---

def is_simulation_mode() -> bool:
    """
    Checks if the application is running in simulation mode due to missing API keys.
    Returns True if any key is missing, False otherwise.
    """
    if not ALPHA_VANTAGE_API_KEY or ALPHA_VANTAGE_API_KEY == "YOUR_ALPHA_VANTAGE_API_KEY":
        logger.warning("ALPHA_VANTAGE_API_KEY is not configured.")
        return True
    if not NEWS_API_KEY or NEWS_API_KEY == "YOUR_NEWS_API_KEY":
        logger.warning("NEWS_API_KEY is not configured.")
        return True
    return False

# Log the current operating mode
if is_simulation_mode():
    logger.warning("Application is running in SIMULATION MODE due to missing API keys.")
else:
    logger.info("All API keys are configured. Application is running in LIVE MODE.")