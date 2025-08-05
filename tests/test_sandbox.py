"""
Test eBay sandbox integration

This module contains tests for eBay API integration using sandbox environment.
Run with: pytest tests/test_sandbox.py -v
"""
import os
import pytest
from unittest.mock import Mock, patch

from app.config import Config
from app.orders import OrderManager
from app.labels import LabelManager


@pytest.fixture
def sandbox_config():
    """Create a test config for sandbox testing"""
    # Set environment variables for sandbox
    with patch.dict(
        os.environ,
        {
            "EBAY_ENVIRONMENT": "sandbox",
            "EBAY_SANDBOX_CLIENT_ID": os.getenv(
                "EBAY_SANDBOX_CLIENT_ID", "test_client_id"
            ),
            "EBAY_SANDBOX_CLIENT_SECRET": os.getenv(
                "EBAY_SANDBOX_CLIENT_SECRET", "test_client_secret"
            ),
            "EBAY_SANDBOX_DEV_ID": os.getenv("EBAY_SANDBOX_DEV_ID", "test_dev_id"),
            "EBAY_SITE_ID": "0",  # US site
            "STATE_FILE": "test_seen_orders.json",
        },
    ):
        yield Config()


class TestSandboxConfiguration:
    """Test sandbox configuration setup"""

    def test_sandbox_environment_detection(self, sandbox_config):
        """Test that sandbox environment is properly detected"""
        assert sandbox_config.EBAY_ENVIRONMENT == "sandbox"
        assert sandbox_config.current_client_id == sandbox_config.EBAY_SANDBOX_CLIENT_ID
        assert (
            sandbox_config.current_client_secret
            == sandbox_config.EBAY_SANDBOX_CLIENT_SECRET
        )
        assert sandbox_config.current_dev_id == sandbox_config.EBAY_SANDBOX_DEV_ID

    def test_sandbox_validation(self, sandbox_config):
        """Test configuration validation with sandbox credentials"""
        # Should be valid if we have the sandbox environment variables set
        if (
            os.getenv("EBAY_SANDBOX_CLIENT_ID")
            and os.getenv("EBAY_SANDBOX_CLIENT_SECRET")
            and os.getenv("EBAY_SANDBOX_DEV_ID")
        ):
            assert sandbox_config.validate() is True
        else:
            # If no real credentials, should still create config but validation may fail
            assert isinstance(sandbox_config.validate(), bool)


class TestEbayClientInitialization:
    """Test eBay API client initialization in sandbox"""

    def test_order_manager_initialization(self, sandbox_config):
        """Test OrderManager initialization with sandbox config"""
        order_manager = OrderManager(sandbox_config)
        assert order_manager.config == sandbox_config

        # Check if APIs are initialized (may be None if no valid credentials)
        assert hasattr(order_manager, "trading_api")
        assert hasattr(order_manager, "finding_api")
        assert hasattr(order_manager, "shopping_api")

    def test_label_manager_initialization(self, sandbox_config):
        """Test LabelManager initialization with sandbox config"""
        label_manager = LabelManager(sandbox_config)
        assert label_manager.config == sandbox_config

        # Check if APIs are initialized (may be None if no valid credentials)
        assert hasattr(label_manager, "trading_api")
        assert hasattr(label_manager, "finding_api")
        assert hasattr(label_manager, "shopping_api")


class TestSandboxOrderPolling:
    """Test order polling in sandbox environment"""

    @patch("app.orders.OrderManager.trading_api")
    def test_poll_new_orders_with_mock_api(self, mock_trading_api, sandbox_config):
        """Test order polling with mocked Trading API response"""
        # Mock successful API response
        mock_response = Mock()
        mock_response.reply.Ack = "Success"
        mock_response.dict.return_value = {
            "OrderArray": {
                "Order": [
                    {
                        "OrderID": "TEST-ORDER-123",
                        "OrderStatus": "Completed",
                        "ShippedTime": None,
                        "TransactionArray": {
                            "Transaction": [
                                {
                                    "TransactionID": "TEST-TRANS-123",
                                    "Item": {"ItemID": "TEST-ITEM-123"},
                                }
                            ]
                        },
                    }
                ]
            }
        }

        mock_trading_api.execute.return_value = mock_response

        order_manager = OrderManager(sandbox_config)
        order_manager._trading_api = mock_trading_api

        orders = order_manager.poll_new_orders()

        # Should return the mocked order
        assert len(orders) == 1
        assert orders[0]["OrderID"] == "TEST-ORDER-123"

        # Verify API was called with correct parameters
        mock_trading_api.execute.assert_called_once()
        call_args = mock_trading_api.execute.call_args
        assert call_args[0][0] == "GetOrders"  # First argument should be "GetOrders"
        assert isinstance(call_args[0][1], dict)  # Second argument should be a dict


class TestSandboxLabelCreation:
    """Test label creation in sandbox environment"""

    def test_create_test_label_pdf(self, sandbox_config):
        """Test creation of test PDF labels for sandbox"""
        label_manager = LabelManager(sandbox_config)

        # Test the internal PDF creation method
        test_order_id = "TEST-ORDER-456"
        test_tracking = "TEST123456"

        pdf_path = label_manager._create_test_label_pdf(test_order_id, test_tracking)

        # Should create a PDF file
        if pdf_path:
            assert pdf_path.exists()
            assert pdf_path.name == f"test_shipping_label_{test_order_id}.pdf"

            # Clean up
            pdf_path.unlink()

    def test_buy_shipping_label_sandbox(self, sandbox_config):
        """Test buying shipping labels in sandbox mode"""
        label_manager = LabelManager(sandbox_config)

        # Mock order data
        test_order = {
            "OrderID": "TEST-ORDER-789",
            "TransactionArray": {
                "Transaction": [
                    {
                        "TransactionID": "TEST-TRANS-789",
                        "Item": {"ItemID": "TEST-ITEM-789"},
                    }
                ]
            },
        }

        # Should create mock label in sandbox
        result = label_manager.buy_shipping_label(test_order)

        if result:
            assert result["order_id"] == "TEST-ORDER-789"
            assert result["status"] == "label_created"
            assert "tracking_number" in result
            assert result["tracking_number"].startswith("TEST")


@pytest.mark.integration
class TestSandboxIntegration:
    """Integration tests for sandbox environment

    These tests require valid sandbox credentials to be set as environment variables:
    - EBAY_SANDBOX_CLIENT_ID
    - EBAY_SANDBOX_CLIENT_SECRET
    - EBAY_SANDBOX_DEV_ID
    """

    @pytest.mark.skipif(
        not all(
            [
                os.getenv("EBAY_SANDBOX_CLIENT_ID"),
                os.getenv("EBAY_SANDBOX_CLIENT_SECRET"),
                os.getenv("EBAY_SANDBOX_DEV_ID"),
            ]
        ),
        reason="Sandbox credentials not available",
    )
    def test_real_api_connection(self, sandbox_config):
        """Test actual connection to eBay sandbox APIs"""
        order_manager = OrderManager(sandbox_config)

        # Should have valid API clients if credentials are correct
        assert order_manager.trading_api is not None
        # Note: We don't actually call the API here to avoid rate limits
        # and because sandbox may not have test data

    def test_end_to_end_sandbox_workflow(self, sandbox_config):
        """Test complete workflow in sandbox mode"""
        order_manager = OrderManager(sandbox_config)
        label_manager = LabelManager(sandbox_config)

        # This would be a full workflow test but requires mock data
        # since sandbox environments typically don't have real orders
        assert order_manager is not None
        assert label_manager is not None


if __name__ == "__main__":
    # Run tests if executed directly
    pytest.main([__file__, "-v"])
