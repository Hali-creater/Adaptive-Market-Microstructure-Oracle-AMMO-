# config.py

from utils.helpers import setup_logging

logger = setup_logging()

class Config:
    """
    A simple configuration class to hold API keys and settings provided by the user at runtime.
    """
    def __init__(self, alpha_vantage_api_key: str = None, news_api_key: str = None):
        """
        Initializes the config with the provided API keys.

        Args:
            alpha_vantage_api_key (str, optional): The API key for Alpha Vantage. Defaults to None.
            news_api_key (str, optional): The API key for NewsAPI. Defaults to None.
        """
        logger.info("Initializing configuration with user-provided keys...")

        # --- API Keys ---
        self.ALPHA_VANTAGE_API_KEY = alpha_vantage_api_key
        self.NEWS_API_KEY = news_api_key

        # --- Application Settings ---
        self.APP_TITLE = "AMMO Trading Agent"

        # Log the operating mode
        if self.is_simulation_mode():
            logger.warning("Running in simulation mode due to one or more missing API keys.")
        else:
            logger.info("All necessary API keys are configured. Running in live mode.")

    def is_simulation_mode(self) -> bool:
        """
        Checks if the application should run in simulation mode due to missing API keys.
        """
        # Simulation mode is active if any of the essential keys are missing.
        if not self.ALPHA_VANTAGE_API_KEY or not self.NEWS_API_KEY:
            return True
        return False