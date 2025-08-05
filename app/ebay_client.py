"""
Shared eBay API client functionality
"""
import logging
from typing import Optional, Dict, Any

from ebaysdk.exception import ConnectionError as EbayConnectionError
from ebaysdk.trading import Connection as TradingAPI
from ebaysdk.finding import Connection as FindingAPI
from ebaysdk.shopping import Connection as ShoppingAPI
from .config import Config

logger = logging.getLogger(__name__)


class EbayClientMixin:  # pylint: disable=too-few-public-methods
    """Mixin class for shared eBay API client functionality"""

    def __init__(self, config: Config):
        self.config = config
        self._trading_api = None
        self._finding_api = None
        self._shopping_api = None
        self._init_ebay_apis()

    def _init_ebay_apis(self) -> None:
        """Initialize eBay SDK API clients"""
        try:
            if not self.config.validate():
                logger.error("eBay API configuration is incomplete")
                return

            # Get configuration based on environment
            config_dict = self._get_api_config()

            # Initialize Trading API (for orders and selling)
            self._trading_api = TradingAPI(config_file=None, **config_dict)

            # Initialize Finding API (for searching)
            self._finding_api = FindingAPI(config_file=None, **config_dict)

            # Initialize Shopping API (for item details)
            self._shopping_api = ShoppingAPI(config_file=None, **config_dict)

            logger.info(
                "eBay SDK APIs initialized successfully for %s environment",
                self.config.EBAY_ENVIRONMENT,
            )
        except EbayConnectionError as e:
            logger.error("Failed to initialize eBay APIs: %s", e)
            self._trading_api = None
            self._finding_api = None
            self._shopping_api = None
        except (OSError, ValueError) as e:
            logger.error("Unexpected error initializing eBay APIs: %s", e)
            self._trading_api = None
            self._finding_api = None
            self._shopping_api = None

    def _get_api_config(self) -> Dict[str, Any]:
        """Get API configuration dictionary for ebaysdk"""
        if self.config.EBAY_ENVIRONMENT == "sandbox":
            domain = "api.sandbox.ebay.com"
        else:
            domain = "api.ebay.com"

        return {
            "appid": self.config.current_client_id,
            "devid": self.config.current_dev_id,
            "certid": self.config.current_client_secret,
            "domain": domain,
            "siteid": self.config.EBAY_SITE_ID,
        }

    @property
    def trading_api(self) -> Optional[TradingAPI]:
        """Get the eBay Trading API client"""
        return self._trading_api

    @property
    def finding_api(self) -> Optional[FindingAPI]:
        """Get the eBay Finding API client"""
        return self._finding_api

    @property
    def shopping_api(self) -> Optional[ShoppingAPI]:
        """Get the eBay Shopping API client"""
        return self._shopping_api
