"""
Configuration management for eBay Label Printer

Handles environment variables and settings for:
- eBay API credentials
- CUPS printer configuration
- Application settings
"""

import os
from typing import Optional


class Config:
    """Configuration class for eBay Label Printer"""

    # eBay API Configuration
    EBAY_CLIENT_ID: Optional[str] = os.getenv("EBAY_CLIENT_ID")
    EBAY_CLIENT_SECRET: Optional[str] = os.getenv("EBAY_CLIENT_SECRET")
    EBAY_REFRESH_TOKEN: Optional[str] = os.getenv("EBAY_REFRESH_TOKEN")
    EBAY_ENVIRONMENT: str = os.getenv(
        "EBAY_ENVIRONMENT", "sandbox"
    )  # sandbox or production

    # CUPS Printer Configuration
    CUPS_SERVER_URI: str = os.getenv("CUPS_SERVER_URI", "192.168.8.194")
    PRINTER_NAME: str = os.getenv("PRINTER_NAME", "default")

    # Application Settings
    POLLING_INTERVAL: int = int(
        os.getenv("POLLING_INTERVAL", "300")
    )  # 5 minutes default
    DRY_RUN: bool = os.getenv("DRY_RUN", "false").lower() == "true"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # Data Storage
    STATE_FILE: str = os.getenv("STATE_FILE", "seen_order_ids.json")

    @classmethod
    def validate(cls) -> bool:
        """Validate that required configuration is present"""
        required_fields = [
            cls.EBAY_CLIENT_ID,
            cls.EBAY_CLIENT_SECRET,
            cls.EBAY_REFRESH_TOKEN,
        ]
        return all(field is not None for field in required_fields)
