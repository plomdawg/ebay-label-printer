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

from .config import Config

logger = logging.getLogger(__name__)


class OrderManager:
    """Manages eBay order polling and tracking"""
    
    def __init__(self, config: Config):
        self.config = config
        self.state_file = Path(config.STATE_FILE)
        self._seen_orders: Set[str] = self._load_seen_orders()
    
    def _load_seen_orders(self) -> Set[str]:
        """Load previously seen order IDs from state file"""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r') as f:
                    data = json.load(f)
                    return set(data.get('seen_order_ids', []))
            except (json.JSONDecodeError, IOError) as e:
                logger.warning(f"Could not load state file: {e}")
        return set()
    
    def _save_seen_orders(self) -> None:
        """Save seen order IDs to state file"""
        try:
            with open(self.state_file, 'w') as f:
                json.dump({'seen_order_ids': list(self._seen_orders)}, f)
        except IOError as e:
            logger.error(f"Could not save state file: {e}")
    
    def poll_new_orders(self) -> List[Dict[str, Any]]:
        """
        Poll eBay API for new orders
        
        Returns:
            List of new order dictionaries
        """
        # TODO: Implement eBay API polling
        logger.info("Polling eBay API for new orders...")
        new_orders = []
        
        # Placeholder implementation
        # This will be replaced with actual eBay API calls
        
        return new_orders
    
    def mark_order_processed(self, order_id: str) -> None:
        """Mark an order as processed to avoid reprocessing"""
        self._seen_orders.add(order_id)
        self._save_seen_orders()
        logger.info(f"Marked order {order_id} as processed")
    
    def is_order_seen(self, order_id: str) -> bool:
        """Check if an order has already been processed"""
        return order_id in self._seen_orders