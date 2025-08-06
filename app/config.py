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


class Config:  # pylint: disable=too-few-public-methods
    """Configuration class for eBay Label Printer"""

    def __init__(self) -> None:
        """Initialize configuration with environment variables"""
        # eBay API Configuration - ebaysdk format
        self.EBAY_CLIENT_ID: Optional[str] = os.getenv("EBAY_CLIENT_ID")
        self.EBAY_CLIENT_SECRET: Optional[str] = os.getenv("EBAY_CLIENT_SECRET")
        self.EBAY_DEV_ID: Optional[str] = os.getenv("EBAY_DEV_ID")
        self.EBAY_AUTH_TOKEN: Optional[str] = os.getenv("EBAY_AUTH_TOKEN")

        # Sandbox configuration
        self.EBAY_SANDBOX_CLIENT_ID: Optional[str] = os.getenv("EBAY_SANDBOX_CLIENT_ID")
        self.EBAY_SANDBOX_CLIENT_SECRET: Optional[str] = os.getenv(
            "EBAY_SANDBOX_CLIENT_SECRET"
        )
        self.EBAY_SANDBOX_DEV_ID: Optional[str] = os.getenv("EBAY_SANDBOX_DEV_ID")
        self.EBAY_SANDBOX_AUTH_TOKEN: Optional[str] = os.getenv(
            "EBAY_SANDBOX_AUTH_TOKEN"
        )

        # Environment setting (sandbox or production)
        self.EBAY_ENVIRONMENT: str = os.getenv("EBAY_ENVIRONMENT", "sandbox").lower()
        self.EBAY_SITE_ID: str = os.getenv("EBAY_SITE_ID", "0")  # US site ID

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
        if self.EBAY_ENVIRONMENT == "sandbox":
            required_fields = [
                self.EBAY_SANDBOX_CLIENT_ID,
                self.EBAY_SANDBOX_CLIENT_SECRET,
                self.EBAY_SANDBOX_DEV_ID,
                self.EBAY_SANDBOX_AUTH_TOKEN,
            ]
        else:
            required_fields = [
                self.EBAY_CLIENT_ID,
                self.EBAY_CLIENT_SECRET,
                self.EBAY_DEV_ID,
                self.EBAY_AUTH_TOKEN,
            ]
        return all(field is not None for field in required_fields)

    @property
    def current_client_id(self) -> Optional[str]:
        """Get the client ID for the current environment"""
        return (
            self.EBAY_SANDBOX_CLIENT_ID
            if self.EBAY_ENVIRONMENT == "sandbox"
            else self.EBAY_CLIENT_ID
        )

    @property
    def current_client_secret(self) -> Optional[str]:
        """Get the client secret for the current environment"""
        return (
            self.EBAY_SANDBOX_CLIENT_SECRET
            if self.EBAY_ENVIRONMENT == "sandbox"
            else self.EBAY_CLIENT_SECRET
        )

    @property
    def current_dev_id(self) -> Optional[str]:
        """Get the dev ID for the current environment"""
        return (
            self.EBAY_SANDBOX_DEV_ID
            if self.EBAY_ENVIRONMENT == "sandbox"
            else self.EBAY_DEV_ID
        )

    @property
    def current_auth_token(self) -> Optional[str]:
        """Get the auth token for the current environment"""
        return (
            self.EBAY_SANDBOX_AUTH_TOKEN
            if self.EBAY_ENVIRONMENT == "sandbox"
            else self.EBAY_AUTH_TOKEN
        )
