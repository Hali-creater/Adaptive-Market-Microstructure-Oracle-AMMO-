# utils/helpers.py

import logging
import pandas as pd

def setup_logging(level=logging.INFO):
    """
    Configures a basic logger.
    """
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    return logging.getLogger(__name__)

def format_currency(value):
    """
    Formats a numeric value into a currency string.

    Args:
        value (float or int): The number to format.

    Returns:
        str: A string formatted as currency (e.g., "$1,234.56").
    """
    if value is None:
        return "$0.00"
    return f"${value:,.2f}"

def calculate_percentage_change(initial, final):
    """
    Calculates the percentage change between two numbers.
    """
    if initial == 0:
        return float('inf') if final > 0 else 0
    return ((final - initial) / initial) * 100

# Placeholder for more complex helper functions
# For example, functions to clean or preprocess data could go here.
def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    A placeholder function to clean a DataFrame.
    - Fills missing values
    - Removes duplicates
    """
    df.fillna(method='ffill', inplace=True)
    df.drop_duplicates(inplace=True)
    return df