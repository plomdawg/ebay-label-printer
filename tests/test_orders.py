"""
Tests for order management functionality
"""
# pylint: disable=attribute-defined-outside-init, protected-access, unused-argument
import json
import tempfile
from pathlib import Path
from datetime import datetime, timedelta

import pytest

from app.orders import OrderManager


class TestOrderManager:
    """Test order polling and management"""

    def test_init_creates_manager(self, mock_config, mock_ebay_apis):
        """Test that OrderManager initializes correctly"""
        with tempfile.TemporaryDirectory() as tmpdir:
            state_file = Path(tmpdir) / "test_state.json"
            mock_config.STATE_FILE = str(state_file)

            manager = OrderManager(mock_config)
            assert manager.config == mock_config
            assert isinstance(manager._seen_orders, set)

    def test_load_seen_orders_empty_file(self, mock_config, mock_ebay_apis):
        """Test loading seen orders when state file doesn't exist"""
        with tempfile.TemporaryDirectory() as tmpdir:
            state_file = Path(tmpdir) / "nonexistent.json"
            mock_config.STATE_FILE = str(state_file)

            manager = OrderManager(mock_config)
            assert manager._seen_orders == set()

    def test_load_seen_orders_existing_file(self, mock_config, mock_ebay_apis):
        """Test loading seen orders from existing state file"""
        with tempfile.TemporaryDirectory() as tmpdir:
            state_file = Path(tmpdir) / "test_state.json"

            # Create state file with test data
            test_data = {"seen_order_ids": ["order1", "order2", "order3"]}
            with open(state_file, "w", encoding="utf-8") as f:
                json.dump(test_data, f)

            mock_config.STATE_FILE = str(state_file)
            manager = OrderManager(mock_config)

            assert manager._seen_orders == {
                "order1",
                "order2",
                "order3",
            }

    def test_mark_order_processed(self, mock_config, mock_ebay_apis):
        """Test marking an order as processed"""
        with tempfile.TemporaryDirectory() as tmpdir:
            state_file = Path(tmpdir) / "test_state.json"
            mock_config.STATE_FILE = str(state_file)

            manager = OrderManager(mock_config)
            manager.mark_order_processed("test_order_123")

            assert "test_order_123" in manager._seen_orders

            # Verify it was saved to file
            assert state_file.exists()
            with open(state_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                assert "test_order_123" in data["seen_order_ids"]

    def test_is_order_seen(self, mock_config, mock_ebay_apis):
        """Test checking if order has been seen"""
        with tempfile.TemporaryDirectory() as tmpdir:
            state_file = Path(tmpdir) / "test_state.json"
            mock_config.STATE_FILE = str(state_file)

            manager = OrderManager(mock_config)

            # Initially not seen
            assert not manager.is_order_seen("new_order")

            # After marking as processed
            manager.mark_order_processed("new_order")
            assert manager.is_order_seen("new_order")

    def test_poll_new_orders_placeholder(self, mock_config, mock_ebay_apis):
        """Test placeholder implementation of order polling"""
        with tempfile.TemporaryDirectory() as tmpdir:
            state_file = Path(tmpdir) / "test_state.json"
            mock_config.STATE_FILE = str(state_file)

            manager = OrderManager(mock_config)
            orders = manager.poll_new_orders()

            # Should return empty list when trading API is None (not initialized)
            assert not orders


class TestOrderManagerRealAPI:
    """Test order polling with real eBay API"""

    @pytest.mark.api_sandbox
    def test_poll_new_orders_sandbox(self, real_config_sandbox):
        """Test order polling against eBay sandbox API"""
        with tempfile.TemporaryDirectory() as tmpdir:
            state_file = Path(tmpdir) / "test_state_sandbox.json"
            real_config_sandbox.STATE_FILE = str(state_file)

            manager = OrderManager(real_config_sandbox)

            # This should connect to the real sandbox API
            assert manager.trading_api is not None

            # Poll for orders - sandbox may not have real orders
            orders = manager.poll_new_orders()

            # Assert that we got a valid response (list, even if empty)
            assert isinstance(orders, list)

            print(f"Sandbox API returned {len(orders)} orders")
            for order in orders[:3]:  # Show first 3 orders if any
                order_id = order.get("OrderID", "Unknown")
                status = order.get("OrderStatus", "Unknown")
                print(f"  Order {order_id}: Status={status}")

    @pytest.mark.api_production
    def test_poll_new_orders_production(self, real_config_production):
        """Test order polling against eBay production API"""
        with tempfile.TemporaryDirectory() as tmpdir:
            state_file = Path(tmpdir) / "test_state_production.json"
            real_config_production.STATE_FILE = str(state_file)

            manager = OrderManager(real_config_production)

            # This should connect to the real production API
            assert manager.trading_api is not None

            # Poll for orders - this will get real orders from your account
            orders = manager.poll_new_orders()

            # Assert that we got a valid response (list, even if empty)
            assert isinstance(orders, list)

            print(f"Production API returned {len(orders)} orders")
            for order in orders[:3]:  # Show first 3 orders if any
                order_id = order.get("OrderID", "Unknown")
                status = order.get("OrderStatus", "Unknown")
                buyer = order.get("BuyerUserID", "Unknown")
                total = order.get("Total", {}).get("_value", "Unknown")
                print(
                    f"  Order {order_id}: Status={status}, Buyer={buyer}, Total=${total}"
                )

    @pytest.mark.api_sandbox
    def test_mark_order_processed_sandbox(self, real_config_sandbox):
        """Test marking orders as processed with sandbox API"""
        with tempfile.TemporaryDirectory() as tmpdir:
            state_file = Path(tmpdir) / "test_state_sandbox.json"
            real_config_sandbox.STATE_FILE = str(state_file)

            manager = OrderManager(real_config_sandbox)
            test_order_id = "TEST-SANDBOX-ORDER-123"

            # Initially not seen
            assert not manager.is_order_seen(test_order_id)

            # Mark as processed
            manager.mark_order_processed(test_order_id)

            # Should now be seen
            assert manager.is_order_seen(test_order_id)

            # Verify persistence
            manager2 = OrderManager(real_config_sandbox)
            assert manager2.is_order_seen(test_order_id)

    @pytest.mark.api_production
    def test_mark_order_processed_production(self, real_config_production):
        """Test marking orders as processed with production API"""
        with tempfile.TemporaryDirectory() as tmpdir:
            state_file = Path(tmpdir) / "test_state_production.json"
            real_config_production.STATE_FILE = str(state_file)

            manager = OrderManager(real_config_production)
            test_order_id = "TEST-PRODUCTION-ORDER-456"

            # Initially not seen
            assert not manager.is_order_seen(test_order_id)

            # Mark as processed
            manager.mark_order_processed(test_order_id)

            # Should now be seen
            assert manager.is_order_seen(test_order_id)

            # Verify persistence
            manager2 = OrderManager(real_config_production)
            assert manager2.is_order_seen(test_order_id)

    @pytest.mark.api_production
    def test_fetch_recent_order_production(self, real_config_production):
        """Test fetching the most recent order from production API"""
        with tempfile.TemporaryDirectory() as tmpdir:
            state_file = Path(tmpdir) / "test_recent_order.json"
            real_config_production.STATE_FILE = str(state_file)

            manager = OrderManager(real_config_production)

            # Get all orders including already seen ones
            # Temporarily clear seen orders to get everything
            original_seen = manager._seen_orders.copy()
            manager._seen_orders.clear()

            try:
                orders = manager.poll_new_orders()

                if orders:
                    # Sort by creation time to get most recent
                    sorted_orders = sorted(
                        orders, key=lambda x: x.get("CreatedTime", ""), reverse=True
                    )

                    most_recent = sorted_orders[0]
                    order_id = most_recent.get("OrderID", "Unknown")
                    created_time = most_recent.get("CreatedTime", "Unknown")
                    buyer = most_recent.get("BuyerUserID", "Unknown")
                    total = most_recent.get("Total", {}).get("_value", "Unknown")

                    print(f"Most recent order: {order_id}")
                    print(f"  Created: {created_time}")
                    print(f"  Buyer: {buyer}")
                    print(f"  Total: ${total}")

                    # Verify order structure has expected fields
                    assert "OrderID" in most_recent
                    assert "OrderStatus" in most_recent
                    assert "CreatedTime" in most_recent

                else:
                    print("No orders found in the last 7 days")

            finally:
                # Restore original seen orders
                manager._seen_orders = original_seen

    @pytest.mark.api_production
    def test_debug_all_orders_production(self, real_config_production):
        """Debug test to show ALL orders without filtering"""
        with tempfile.TemporaryDirectory() as tmpdir:
            state_file = Path(tmpdir) / "test_debug_orders.json"
            real_config_production.STATE_FILE = str(state_file)

            manager = OrderManager(real_config_production)

            if not manager.trading_api:
                print("Trading API not initialized")
                return

            # Get orders from the last 7 days without any filtering
            from_date = datetime.now() - timedelta(days=7)

            # Try different order status values to see what exists
            for order_status in ["Active", "Completed", "All"]:
                print(f"\n=== Testing OrderStatus: {order_status} ===")

                api_request = {
                    "CreateTimeFrom": from_date.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
                    "CreateTimeTo": datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z"),
                    "OrderStatus": order_status,
                    "Pagination": {"EntriesPerPage": 50, "PageNumber": 1},
                }

                # Remove ListingType filter to see all types
                response = manager.trading_api.execute("GetOrders", api_request)

                orders = OrderManager.extract_orders_from_response(response)
                print(f"Found {len(orders)} orders with status '{order_status}'")

                for order in orders:
                    print(f"  Order {order.get('OrderID', 'Unknown')}:")
                    print(f"    Status: {order.get('OrderStatus', 'Unknown')}")
                    print(f"    Created: {order.get('CreatedTime', 'Unknown')}")
                    print(f"    Buyer: {order.get('BuyerUserID', 'Unknown')}")
                    print(
                        f"    Total: ${order.get('Total', {}).get('_value', 'Unknown')}"
                    )
                    print(f"    Shipped: {order.get('ShippedTime', 'None')}")
                    print(f"    ListingType: {order.get('ListingType', 'Unknown')}")
                    print()

                print(f"=== End {order_status} ===\n")
