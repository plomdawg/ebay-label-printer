"""
Tests for order management functionality
"""
# pylint: disable=protected-access, attribute-defined-outside-init
import json
import tempfile
from pathlib import Path

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
