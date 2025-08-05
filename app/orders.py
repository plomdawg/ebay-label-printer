"""
eBay order polling and management

Handles:
- Polling eBay Sell API for new orders
- Tracking seen orders to avoid duplicates
- Order data parsing and validation
"""

import json
import logging
from typing import List, Dict, Any, Set
from pathlib import Path
from datetime import datetime, timedelta

from ebay_rest import Error as EbayError
from .config import Config
from .ebay_client import EbayClientMixin

logger = logging.getLogger(__name__)


class OrderManager(EbayClientMixin):
    """Manages eBay order polling and tracking"""

    def __init__(self, config: Config):
        self.state_file = Path(config.STATE_FILE)
        self._seen_orders: Set[str] = self._load_seen_orders()
        super().__init__(config)

    def _load_seen_orders(self) -> Set[str]:
        """Load previously seen order IDs from state file"""
        if self.state_file.exists():
            try:
                with open(self.state_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return set(data.get("seen_order_ids", []))
            except (json.JSONDecodeError, IOError) as e:
                logger.warning("Could not load state file: %s", e)
        return set()

    def _save_seen_orders(self) -> None:
        """Save seen order IDs to state file"""
        try:
            with open(self.state_file, "w", encoding="utf-8") as f:
                json.dump({"seen_order_ids": list(self._seen_orders)}, f)
        except IOError as e:
            logger.error("Could not save state file: %s", e)

    def poll_new_orders(self) -> List[Dict[str, Any]]:
        """
        Poll eBay API for new orders

        Returns:
            List of new order dictionaries
        """
        logger.info("Polling eBay API for new orders...")
        new_orders: List[Dict[str, Any]] = []

        if not self.api:
            logger.warning("eBay API not initialized, returning empty list")
            return new_orders

        try:
            # Get orders from the last 24 hours to catch any recent orders
            from_date = datetime.now() - timedelta(days=1)

            # Use the sell_fulfillment_get_orders method from ebay-rest
            # Note: This searches for orders that need fulfillment
            orders_response = self.api.sell_fulfillment_get_orders(
                filter_creation_date_range_from=from_date.isoformat() + "Z",
                limit=50,  # Reasonable batch size
            )

            for order_record in orders_response:
                if "record" not in order_record:
                    continue

                order = order_record["record"]
                order_id = order.get("orderId", "")

                # Skip if we've already processed this order
                if self.is_order_seen(order_id):
                    continue

                # Only process orders that are ready to ship
                order_fulfillment_status = order.get(
                    "orderFulfillmentStatus", "NOT_STARTED"
                )
                if order_fulfillment_status in ["NOT_STARTED", "IN_PROGRESS"]:
                    new_orders.append(order)
                    logger.info("Found new order %s", order_id)

        except EbayError as e:
            logger.error("eBay API error while polling orders: %s", e)
        except (OSError, ValueError, KeyError) as e:
            logger.error("Unexpected error while polling orders: %s", e)

        logger.info("Found %d new orders", len(new_orders))
        return new_orders

    def mark_order_processed(self, order_id: str) -> None:
        """Mark an order as processed to avoid reprocessing"""
        self._seen_orders.add(order_id)
        self._save_seen_orders()
        logger.info("Marked order %s as processed", order_id)

    def is_order_seen(self, order_id: str) -> bool:
        """Check if an order has already been processed"""
        return order_id in self._seen_orders
