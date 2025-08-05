"""
Tests for configuration management
"""

import os
from unittest.mock import patch

from app.config import Config


class TestConfig:
    """Test configuration handling"""

    def test_default_values(self):
        """Test that default configuration values are set correctly"""
        config = Config()

        assert config.CUPS_SERVER_URI == "192.168.8.194"
        assert config.PRINTER_NAME == "Thermal-Printer"
        assert config.POLLING_INTERVAL == 300
        assert config.DRY_RUN is False
        assert config.LOG_LEVEL == "INFO"
        assert config.STATE_FILE == "seen_order_ids.json"

    @patch.dict(
        os.environ,
        {
            "EBAY_CLIENT_ID": "test_client_id",
            "EBAY_CLIENT_SECRET": "test_client_secret",
            "EBAY_REFRESH_TOKEN": "test_refresh_token",
            "CUPS_SERVER_URI": "192.168.1.100",
            "PRINTER_NAME": "test_printer",
            "POLLING_INTERVAL": "600",
            "DRY_RUN": "true",
            "LOG_LEVEL": "DEBUG",
            "STATE_FILE": "custom_state.json",
        },
    )
    def test_environment_variables(self):
        """Test that environment variables override defaults"""
        config = Config()

        assert config.EBAY_CLIENT_ID == "test_client_id"
        assert config.EBAY_CLIENT_SECRET == "test_client_secret"
        assert config.EBAY_REFRESH_TOKEN == "test_refresh_token"

        assert config.CUPS_SERVER_URI == "192.168.1.100"
        assert config.PRINTER_NAME == "test_printer"
        assert config.POLLING_INTERVAL == 600
        assert config.DRY_RUN is True
        assert config.LOG_LEVEL == "DEBUG"
        assert config.STATE_FILE == "custom_state.json"

    @patch.dict(
        os.environ,
        {
            "EBAY_CLIENT_ID": "test_client_id",
            "EBAY_CLIENT_SECRET": "test_client_secret",
            "EBAY_REFRESH_TOKEN": "test_refresh_token",
        },
    )
    def test_validate_complete_config(self):
        """Test validation with all required fields"""
        config = Config()
        assert config.validate() is True

    def test_validate_incomplete_config(self):
        """Test validation with missing required fields"""
        with patch.dict(os.environ, {}, clear=True):
            config = Config()
            assert config.validate() is False

    @patch.dict(os.environ, {"EBAY_SANDBOX_CLIENT_ID": "test_client_id"}, clear=True)
    def test_validate_partial_config(self):
        """Test validation with only some required fields (missing other sandbox fields)"""
        config = Config()
        # Should fail because it only has client_id but missing client_secret and dev_id for sandbox
        assert config.validate() is False
