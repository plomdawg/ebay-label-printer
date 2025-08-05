"""
Configuration management for eBay Label Printer

Handles environment variables and settings for:
- eBay API credentials
- CUPS printer configuration
- Application settings
"""
# pylint: disable=too-many-instance-attributes, invalid-name

import os
from typing import Optional


class Config:
    """Configuration class for eBay Label Printer"""

    def __init__(self) -> None:
        """Initialize configuration with environment variables"""
        # eBay API Configuration
        self.EBAY_CLIENT_ID: Optional[str] = os.getenv("EBAY_CLIENT_ID")
        self.EBAY_CLIENT_SECRET: Optional[str] = os.getenv("EBAY_CLIENT_SECRET")
        self.EBAY_REFRESH_TOKEN: Optional[str] = os.getenv("EBAY_REFRESH_TOKEN")
        self.EBAY_ENVIRONMENT: str = os.getenv(
            "EBAY_ENVIRONMENT", "sandbox"
        )  # sandbox or production

        # CUPS Printer Configuration
        self.CUPS_SERVER_URI: str = os.getenv("CUPS_SERVER_URI", "192.168.8.194")
        self.PRINTER_NAME: str = os.getenv("PRINTER_NAME", "default")
        self.PRINT_COPIES: int = int(os.getenv("PRINT_COPIES", "1"))
        self.PRINT_DUPLEX: bool = os.getenv("PRINT_DUPLEX", "false").lower() == "true"
        self.PAPER_SIZE: str = os.getenv("PAPER_SIZE", "Letter")  # Letter, A4, etc.

        # Application Settings
        self.POLLING_INTERVAL: int = int(
            os.getenv("POLLING_INTERVAL", "300")
        )  # 5 minutes default
        self.DRY_RUN: bool = os.getenv("DRY_RUN", "false").lower() == "true"
        self.LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

        # Data Storage
        self.STATE_FILE: str = os.getenv("STATE_FILE", "seen_order_ids.json")

    def validate(self) -> bool:
        """Validate that required configuration is present"""
        required_fields = [
            self.EBAY_CLIENT_ID,
            self.EBAY_CLIENT_SECRET,
            self.EBAY_REFRESH_TOKEN,
        ]
        return all(field is not None for field in required_fields)

    def get_ebay_api_base_url(self) -> str:
        """Get the eBay API base URL based on environment"""
        if self.EBAY_ENVIRONMENT == "production":
            return "https://api.ebay.com"
        return "https://api.sandbox.ebay.com"
