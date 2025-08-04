"""
Tests for order management functionality
"""

import json
import tempfile
from pathlib import Path
from unittest.mock import Mock


from app.orders import OrderManager
from app.config import Config


class TestOrderManager:
    """Test order polling and management"""

    def setup_method(self):
        """Set up test fixtures"""
        self.config = Mock(spec=Config)
        self.config.STATE_FILE = "test_state.json"

    def test_init_creates_manager(self):
        """Test that OrderManager initializes correctly"""
        with tempfile.TemporaryDirectory() as tmpdir:
            state_file = Path(tmpdir) / "test_state.json"
            self.config.STATE_FILE = str(state_file)

            manager = OrderManager(self.config)
            assert manager.config == self.config
            assert isinstance(manager._seen_orders, set)

    def test_load_seen_orders_empty_file(self):
        """Test loading seen orders when state file doesn't exist"""
        with tempfile.TemporaryDirectory() as tmpdir:
            state_file = Path(tmpdir) / "nonexistent.json"
            self.config.STATE_FILE = str(state_file)

            manager = OrderManager(self.config)
            assert manager._seen_orders == set()

    def test_load_seen_orders_existing_file(self):
        """Test loading seen orders from existing state file"""
        with tempfile.TemporaryDirectory() as tmpdir:
            state_file = Path(tmpdir) / "test_state.json"

            # Create state file with test data
            test_data = {"seen_order_ids": ["order1", "order2", "order3"]}
            with open(state_file, "w") as f:
                json.dump(test_data, f)

            self.config.STATE_FILE = str(state_file)
            manager = OrderManager(self.config)

            assert manager._seen_orders == {"order1", "order2", "order3"}

    def test_mark_order_processed(self):
        """Test marking an order as processed"""
        with tempfile.TemporaryDirectory() as tmpdir:
            state_file = Path(tmpdir) / "test_state.json"
            self.config.STATE_FILE = str(state_file)

            manager = OrderManager(self.config)
            manager.mark_order_processed("test_order_123")

            assert "test_order_123" in manager._seen_orders

            # Verify it was saved to file
            assert state_file.exists()
            with open(state_file, "r") as f:
                data = json.load(f)
                assert "test_order_123" in data["seen_order_ids"]

    def test_is_order_seen(self):
        """Test checking if order has been seen"""
        with tempfile.TemporaryDirectory() as tmpdir:
            state_file = Path(tmpdir) / "test_state.json"
            self.config.STATE_FILE = str(state_file)

            manager = OrderManager(self.config)

            # Initially not seen
            assert not manager.is_order_seen("new_order")

            # After marking as processed
            manager.mark_order_processed("new_order")
            assert manager.is_order_seen("new_order")

    def test_poll_new_orders_placeholder(self):
        """Test placeholder implementation of order polling"""
        with tempfile.TemporaryDirectory() as tmpdir:
            state_file = Path(tmpdir) / "test_state.json"
            self.config.STATE_FILE = str(state_file)

            manager = OrderManager(self.config)
            orders = manager.poll_new_orders()

            # Placeholder should return empty list
            assert not orders
