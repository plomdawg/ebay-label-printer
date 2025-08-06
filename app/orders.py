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

from ebaysdk.exception import ConnectionError as EbayConnectionError
from .config import Config
from .ebay_client import EbayClientMixin

logger = logging.getLogger(__name__)


class OrderManager(EbayClientMixin):
    """Manages eBay order polling and tracking"""

    def __init__(self, config: Config):
        self.state_file = Path(config.STATE_FILE)
        self._seen_orders: Set[str] = self._load_seen_orders()
        super().__init__(config)

    @staticmethod
    def extract_orders_from_response(response) -> List[Dict[str, Any]]:
        """
        Extract orders from eBay API response.

        Args:
            response: eBay API response object

        Returns:
            List of order dictionaries
        """
        orders = []
        if response.reply.Ack in ["Success", "Warning"]:
            orders_array = response.dict().get("OrderArray")
            if orders_array and isinstance(orders_array, dict):
                orders = orders_array.get("Order", [])

            # Handle single order case (not in array)
            if isinstance(orders, dict):
                orders = [orders]

        return orders

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

        if not self.trading_api:
            logger.warning("eBay Trading API not initialized, returning empty list")
            return new_orders

        try:
            # Get orders from the last 7 days to catch any recent orders
            from_date = datetime.now() - timedelta(days=7)
            to_date = datetime.now()

            # Use GetOrders call from Trading API - ebaysdk handles authentication
            api_request = {
                "CreateTimeFrom": from_date.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
                "CreateTimeTo": to_date.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
                "OrderStatus": "Active",  # Get active orders that need fulfillment
                "ListingType": "FixedPriceItem",  # Focus on Buy It Now items
                "Pagination": {"EntriesPerPage": 50, "PageNumber": 1},
            }

            response = self.trading_api.execute("GetOrders", api_request)

            orders = self.extract_orders_from_response(response)
            for order in orders:
                order_id = order.get("OrderID", "")

                # Skip if we've already processed this order
                if self.is_order_seen(order_id):
                    continue

                # Check if order needs fulfillment
                order_status = order.get("OrderStatus", "")
                shipped_time = order.get("ShippedTime")

                # Only process orders that are completed but not yet shipped
                if order_status == "Completed" and not shipped_time:
                    new_orders.append(order)
                    logger.info("Found new order %s", order_id)

        except EbayConnectionError as e:
            logger.error("eBay API connection error while polling orders: %s", e)
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
