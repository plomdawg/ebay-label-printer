"""
eBay order polling and management

Handles:
- Polling eBay Sell API for new orders
- Order data parsing and validation
- Filtering orders based on API status
"""

import logging
from typing import List, Dict, Any
from datetime import datetime, timedelta

from ebaysdk.exception import ConnectionError as EbayConnectionError
from .ebay_client import EbayClientMixin

logger = logging.getLogger(__name__)


class OrderManager(EbayClientMixin):
    """Manages eBay order polling and status-based filtering"""

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

    def poll_new_orders(self) -> List[Dict[str, Any]]:
        """
        Poll eBay API for orders needing fulfillment

        Returns:
            List of order dictionaries that need labels purchased and printed
        """
        logger.info("Polling eBay API for orders needing fulfillment...")
        orders_needing_fulfillment: List[Dict[str, Any]] = []

        if not self.trading_api:
            logger.warning("eBay Trading API not initialized, returning empty list")
            return orders_needing_fulfillment

        try:
            # Get orders from the last 7 days to catch any recent orders
            from_date = datetime.now() - timedelta(days=7)
            to_date = datetime.now()

            # Use GetOrders call from Trading API - ebaysdk handles authentication
            api_request = {
                "CreateTimeFrom": from_date.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
                "CreateTimeTo": to_date.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
                "OrderStatus": "Completed",  # Get completed orders
                "ListingType": "FixedPriceItem",  # Focus on Buy It Now items
                "Pagination": {"EntriesPerPage": 50, "PageNumber": 1},
            }

            response = self.trading_api.execute("GetOrders", api_request)

            orders = self.extract_orders_from_response(response)
            for order in orders:
                order_id = order.get("OrderID", "")

                # Check if order needs fulfillment
                order_status = order.get("OrderStatus", "")
                shipped_time = order.get("ShippedTime")

                # Only process orders that are completed but not yet shipped
                # Once we buy and print a label, the order status should change to Shipped
                if order_status == "Completed" and not shipped_time:
                    orders_needing_fulfillment.append(order)
                    logger.info("Found order needing fulfillment: %s", order_id)

        except EbayConnectionError as e:
            logger.error("eBay API connection error while polling orders: %s", e)
        except (OSError, ValueError, KeyError) as e:
            logger.error("Unexpected error while polling orders: %s", e)

        logger.info(
            "Found %d orders needing fulfillment", len(orders_needing_fulfillment)
        )
        return orders_needing_fulfillment
