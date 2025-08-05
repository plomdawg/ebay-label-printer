"""
Shared eBay API client functionality
"""
import logging
from typing import Optional

from ebay_rest import API, Error as EbayError
from .config import Config

logger = logging.getLogger(__name__)


class EbayClientMixin:
    """Mixin class for shared eBay API client functionality"""

    def __init__(self, config: Config):
        self.config = config
        self._api = None
        self._init_ebay_api()

    def _init_ebay_api(self) -> None:
        """Initialize eBay REST API client"""
        try:
            if not self.config.validate():
                logger.error("eBay API configuration is incomplete")
                return

            self._api = API(
                application=self.config.EBAY_APPLICATION_CONFIG,
                user=self.config.EBAY_USER_CONFIG,
                header=self.config.EBAY_SITE_ID,
            )
            logger.info("eBay API client initialized successfully")
        except EbayError as e:
            logger.error("Failed to initialize eBay API: %s", e)
            self._api = None
        except (OSError, ValueError) as e:
            logger.error("Unexpected error initializing eBay API: %s", e)
            self._api = None

    @property
    def api(self) -> Optional[API]:
        """Get the eBay API client"""
        return self._api
