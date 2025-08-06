"""
Pytest configuration and fixtures for eBay Label Printer tests
"""

import os
from unittest.mock import Mock, patch
import pytest
from app.config import Config


@pytest.fixture
def mock_ebay_apis():
    """Mock all eBay SDK APIs for testing"""
    with patch("app.ebay_client.TradingAPI") as mock_trading, patch(
        "app.ebay_client.FindingAPI"
    ) as mock_finding, patch("app.ebay_client.ShoppingAPI") as mock_shopping:
        yield {
            "trading": mock_trading,
            "finding": mock_finding,
            "shopping": mock_shopping,
        }


@pytest.fixture
def mock_config():
    """Create a mock Config object with all required attributes"""
    config = Mock(spec=Config)
    config.STATE_FILE = "test_state.json"
    config.EBAY_ENVIRONMENT = "sandbox"
    config.EBAY_SITE_ID = "0"
    config.current_client_id = "test_client_id"
    config.current_dev_id = "test_dev_id"
    config.current_client_secret = "test_client_secret"
    config.validate.return_value = True
    return config


@pytest.fixture
def real_config_sandbox():
    """Create a real Config object for sandbox API testing"""
    # Set environment to sandbox for testing
    os.environ["EBAY_ENVIRONMENT"] = "sandbox"
    config = Config()

    # Skip test if required environment variables are not set
    if not config.validate():
        pytest.skip("Sandbox eBay API credentials not configured")

    return config


@pytest.fixture
def real_config_production():
    """Create a real Config object for production API testing"""
    # Set environment to production for testing
    os.environ["EBAY_ENVIRONMENT"] = "production"
    config = Config()

    # Skip test if required environment variables are not set
    if not config.validate():
        pytest.skip("Production eBay API credentials not configured")

    return config
