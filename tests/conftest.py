"""
Pytest configuration and fixtures for eBay Label Printer tests
"""

import pytest
from unittest.mock import Mock, patch
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
    config.EBAY_REFRESH_TOKEN = "test_refresh_token"
    config.validate.return_value = True
    return config
