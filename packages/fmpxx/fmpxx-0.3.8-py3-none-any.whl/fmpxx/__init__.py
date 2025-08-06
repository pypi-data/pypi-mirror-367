from .base import _BaseClient
from .financials import Financials
from .stocks import Stocks

class FMPClient(_BaseClient):
    """Main client for interacting with the Financial Modeling Prep (FMP) API.

    This class provides a user-friendly and consistent interface to access
    various financial data endpoints offered by FMP.

    Args:
        api_key (str | None): Your FMP API key.
        timeout (int, optional): Request timeout in seconds. Defaults to 10.

    Attributes:
        financials (Financials): Access to company fundamental data.
        stocks (Stocks): Access to stock market data.
    """

    def __init__(self, api_key: str | None, timeout: int = 10):
        super().__init__(api_key, timeout)

        # Initialize categorized API modules
        self.financials = Financials(api_key, timeout)
        self.stocks = Stocks(api_key, timeout)

    # You can add more categorized properties here as you implement more modules
    # For example:
    # @property
    # def forex(self):
    #     return Forex(self.api_key, self.timeout, self.output_format)

    # @property
    # def cryptocurrencies(self):
    #     return Cryptocurrencies(self.api_key, self.timeout, self.output_format)