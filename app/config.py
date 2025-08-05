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
        # eBay API Configuration - ebay-rest format
        self.EBAY_CLIENT_ID: Optional[str] = os.getenv("EBAY_CLIENT_ID")
        self.EBAY_CLIENT_SECRET: Optional[str] = os.getenv("EBAY_CLIENT_SECRET")
        self.EBAY_REFRESH_TOKEN: Optional[str] = os.getenv("EBAY_REFRESH_TOKEN")

        # ebay-rest specific configuration
        self.EBAY_APPLICATION_CONFIG: str = os.getenv(
            "EBAY_APPLICATION_CONFIG", "production_1"
        )
        self.EBAY_USER_CONFIG: str = os.getenv("EBAY_USER_CONFIG", "production_1")
        self.EBAY_SITE_ID: str = os.getenv(
            "EBAY_SITE_ID", "US"
        )  # Market/site identifier

        # CUPS Printer Configuration
        self.CUPS_SERVER_URI: str = os.getenv("CUPS_SERVER_URI", "192.168.8.194")
        self.PRINTER_NAME: str = os.getenv("PRINTER_NAME", "Thermal-Printer")

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
