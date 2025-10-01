# modules/risk_manager.py

from utils.constants import MAX_RISK_PER_TRADE, MAX_DRAWDOWN
from utils.helpers import setup_logging, format_currency

logger = setup_logging()

class RiskManager:
    """
    Manages portfolio risk, including position sizing and drawdown monitoring.
    """

    def __init__(self, portfolio_value: float, max_risk_per_trade=MAX_RISK_PER_TRADE, max_drawdown=MAX_DRAWDOWN):
        """
        Initializes the Risk Manager.

        Args:
            portfolio_value (float): The total value of the portfolio.
            max_risk_per_trade (float): The maximum percentage of the portfolio to risk on a single trade.
            max_drawdown (float): The maximum percentage the portfolio is allowed to fall from its peak.
        """
        self.portfolio_value = portfolio_value
        self.max_risk_per_trade = max_risk_per_trade
        self.max_drawdown = max_drawdown
        self.peak_portfolio_value = portfolio_value
        logger.info(f"Risk Manager initialized with portfolio value: {format_currency(self.portfolio_value)}")

    def calculate_position_size(self, entry_price: float, stop_loss_price: float) -> int:
        """
        Calculates the number of shares to purchase based on risk parameters.

        Args:
            entry_price (float): The price at which the asset is bought.
            stop_loss_price (float): The price at which the trade will be exited to limit losses.

        Returns:
            int: The number of shares to buy. Returns 0 if risk is too high or prices are invalid.
        """
        if entry_price <= 0 or stop_loss_price <= 0:
            logger.warning("Invalid entry or stop-loss price (must be > 0). Cannot calculate position size.")
            return 0

        # Amount to risk per trade in currency
        risk_amount = self.portfolio_value * self.max_risk_per_trade

        # Risk per share (absolute difference)
        risk_per_share = abs(entry_price - stop_loss_price)

        if risk_per_share <= 0:
            logger.warning("Entry price and stop-loss price cannot be the same.")
            return 0

        position_size = int(risk_amount / risk_per_share)

        logger.info(f"Calculated position size: {position_size} shares.")
        return position_size

    def calculate_target_price(self, entry_price: float, stop_loss_price: float, risk_reward_ratio: float = 2.0) -> float:
        """
        Calculates the target price for a trade to achieve a specific risk/reward ratio.

        Args:
            entry_price (float): The price at which the asset is bought or sold short.
            stop_loss_price (float): The price at which the trade will be exited to limit losses.
            risk_reward_ratio (float): The desired ratio of reward to risk (e.g., 2.0 for a 1:2 ratio).

        Returns:
            float: The calculated target price. Returns 0 if prices are invalid.
        """
        risk_per_share = abs(entry_price - stop_loss_price)
        if risk_per_share <= 0:
            return 0

        reward_per_share = risk_per_share * risk_reward_ratio

        # For a long position (buy), the stop-loss is below the entry price
        if entry_price > stop_loss_price:
            target_price = entry_price + reward_per_share
        # For a short position (sell), the stop-loss is above the entry price
        else:
            target_price = entry_price - reward_per_share

        logger.info(f"Calculated target price: {format_currency(target_price)} for a 1:{risk_reward_ratio} risk/reward.")
        return target_price

    def check_drawdown(self, current_portfolio_value: float) -> bool:
        """
        Checks if the portfolio has exceeded its maximum allowed drawdown.

        Args:
            current_portfolio_value (float): The current total value of the portfolio.

        Returns:
            bool: True if drawdown is exceeded, False otherwise.
        """
        # Update peak value
        if current_portfolio_value > self.peak_portfolio_value:
            self.peak_portfolio_value = current_portfolio_value

        drawdown = (self.peak_portfolio_value - current_portfolio_value) / self.peak_portfolio_value

        if drawdown > self.max_drawdown:
            logger.critical(
                f"MAX DRAWDOWN EXCEEDED: {drawdown:.2%} > {self.max_drawdown:.2%}. "
                f"Peak value: {format_currency(self.peak_portfolio_value)}, "
                f"Current value: {format_currency(current_portfolio_value)}"
            )
            return True

        return False