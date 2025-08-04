#!/usr/bin/env python3
"""
Main entry point for eBay Label Printer application

Orchestrates the full automation cycle:
1. Poll eBay for new orders
2. Buy shipping labels
3. Generate packing slips
4. Print both documents
"""

import logging
import sys
import time
from pathlib import Path

from app.config import Config
from app.orders import OrderManager
from app.labels import LabelManager
from app.packing import PackingSlipGenerator
from app.print import PrintManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ebay_printer.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


def main():
    """Main application loop"""
    logger.info("Starting eBay Label Printer application")
    
    # Load configuration
    config = Config()
    
    # Validate configuration
    if not config.validate():
        logger.error("Invalid configuration. Check your environment variables.")
        sys.exit(1)
    
    # Initialize components
    order_manager = OrderManager(config)
    label_manager = LabelManager(config)
    packing_generator = PackingSlipGenerator(config)
    print_manager = PrintManager(config)
    
    # Test printer connection
    if not print_manager.test_printer_connection():
        logger.warning("Could not connect to printer. Continuing in dry-run mode.")
        config.DRY_RUN = True
    
    logger.info(f"Application started. Polling interval: {config.POLLING_INTERVAL}s")
    logger.info(f"Dry run mode: {config.DRY_RUN}")
    
    try:
        while True:
            process_orders(order_manager, label_manager, packing_generator, print_manager)
            
            logger.info(f"Sleeping for {config.POLLING_INTERVAL} seconds...")
            time.sleep(config.POLLING_INTERVAL)
            
    except KeyboardInterrupt:
        logger.info("Application stopped by user")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)


def process_orders(order_manager, label_manager, packing_generator, print_manager):
    """Process new orders through the full pipeline"""
    logger.info("Checking for new orders...")
    
    try:
        # Get new orders
        new_orders = order_manager.poll_new_orders()
        
        if not new_orders:
            logger.info("No new orders found")
            return
        
        logger.info(f"Found {len(new_orders)} new orders")
        
        for order in new_orders:
            order_id = order.get('order_id', 'unknown')
            logger.info(f"Processing order {order_id}")
            
            try:
                # Skip if already processed
                if order_manager.is_order_seen(order_id):
                    logger.info(f"Order {order_id} already processed, skipping")
                    continue
                
                # Buy shipping label
                label_info = label_manager.buy_shipping_label(order)
                if not label_info:
                    logger.error(f"Failed to buy label for order {order_id}")
                    continue
                
                # Generate packing slip
                packing_slip_path = packing_generator.generate_packing_slip(order)
                if not packing_slip_path:
                    logger.error(f"Failed to generate packing slip for order {order_id}")
                    continue
                
                # Print documents
                pdf_paths = [Path(label_info['pdf_path']), packing_slip_path]
                success = print_manager.print_documents(pdf_paths)
                
                if success:
                    order_manager.mark_order_processed(order_id)
                    logger.info(f"Successfully processed order {order_id}")
                else:
                    logger.error(f"Failed to print documents for order {order_id}")
                
            except Exception as e:
                logger.error(f"Error processing order {order_id}: {e}")
                continue
                
    except Exception as e:
        logger.error(f"Error during order processing: {e}")


if __name__ == "__main__":
    main()