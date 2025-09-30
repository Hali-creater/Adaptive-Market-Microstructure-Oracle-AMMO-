# config.py

import os
from dotenv import load_dotenv
from utils.helpers import setup_logging

logger = setup_logging()

# Load environment variables from a .env file
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
    logger.info(".env file loaded successfully.")
else:
    logger.warning(".env file not found. Please create one with your API keys.")

# --- API Keys ---
ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
ALPACA_API_KEY = os.getenv("ALPACA_API_KEY")
ALPACA_SECRET_KEY = os.getenv("ALPACA_SECRET_KEY")
ALPACA_BASE_URL = os.getenv("ALPACA_BASE_URL", "https://paper-api.alpaca.markets")

# --- Application Settings ---
APP_TITLE = "AMMO Trading Agent"

# --- Validation ---
def check_api_keys():
    """Checks if essential API keys are configured."""
    keys_configured = True
    if not ALPHA_VANTAGE_API_KEY or ALPHA_VANTAGE_API_KEY == "YOUR_ALPHA_VANTAGE_API_KEY":
        logger.warning("ALPHA_VANTAGE_API_KEY is not configured. Using simulated data.")
        keys_configured = False

    if not NEWS_API_KEY or NEWS_API_KEY == "YOUR_NEWS_API_KEY":
        logger.warning("NEWS_API_KEY is not configured. Using simulated sentiment.")
        keys_configured = False

    return keys_configured

# Run check on import
check_api_keys()