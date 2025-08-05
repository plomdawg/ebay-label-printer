"""
Shipping label management

Handles:
- Purchasing shipping labels via eBay Fulfillment API
- Label refunding if needed
- PDF download and storage
"""
# pylint: disable=useless-return
import logging
from typing import Dict, Any, Optional
from pathlib import Path


from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, landscape

import requests

from ebaysdk.exception import ConnectionError as EbayConnectionError

from .ebay_client import EbayClientMixin

logger = logging.getLogger(__name__)


class LabelManager(EbayClientMixin):
    """Manages shipping label purchasing and handling"""

    def buy_shipping_label(
        self, order_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Buy a shipping label for the given order

        Args:
            order_data: eBay order information

        Returns:
            Label information including PDF path, or None if failed
        """
        order_id = order_data.get("OrderID", "unknown")
        logger.info("Buying shipping label for order %s", order_id)

        if not self.trading_api:
            logger.warning(
                "eBay Trading API not initialized, cannot buy shipping label"
            )
            return None

        try:
            # For sandbox testing, we'll simulate label purchasing
            # In production, this would use eBay's shipping label APIs

            # Extract transaction information from order
            transactions = order_data.get("TransactionArray", {}).get("Transaction", [])
            if not transactions:
                logger.error("No transactions found in order %s", order_id)
                return None

            # Handle single transaction case
            if isinstance(transactions, dict):
                transactions = [transactions]

            transaction = transactions[0]
            transaction_id = transaction.get("TransactionID", "")
            item_id = transaction.get("Item", {}).get("ItemID", "")

            # For sandbox, create a mock shipping label
            mock_tracking_number = f"TEST{order_id[-6:]}"

            # Create mock label data
            label_data = {
                "order_id": order_id,
                "transaction_id": transaction_id,
                "item_id": item_id,
                "tracking_number": mock_tracking_number,
                "carrier": "USPS",
                "service_type": "Priority Mail",
                "status": "label_created",
            }

            # In sandbox mode, we can't actually purchase real labels
            # So we'll create a mock PDF for testing
            if self.config.EBAY_ENVIRONMENT == "sandbox":
                # Create a simple test PDF
                pdf_path = self.create_test_label_pdf(order_id, mock_tracking_number)
                if pdf_path:
                    label_data["pdf_path"] = str(pdf_path)
                    label_data["label_url"] = f"mock://test_label_{order_id}.pdf"
                    logger.info("Created test shipping label for order %s", order_id)
                    return label_data
            else:
                # In production, implement real label purchasing
                logger.warning("Production label purchasing not implemented yet")
                return None

        except EbayConnectionError as e:
            logger.error(
                "eBay API connection error buying label for order %s: %s", order_id, e
            )
        except (OSError, ValueError, KeyError) as e:
            logger.error("Unexpected error buying label for order %s: %s", order_id, e)

        return None

    def download_label_pdf(self, label_url: str, order_id: str) -> Optional[Path]:
        """
        Download label PDF from eBay

        Args:
            label_url: URL to the label PDF
            order_id: Order identifier for filename

        Returns:
            Path to downloaded PDF file, or None if failed
        """
        logger.info("Downloading label PDF for order %s", order_id)

        try:
            # Create data directory if it doesn't exist
            data_dir = Path("data/labels")
            data_dir.mkdir(parents=True, exist_ok=True)

            # Generate filename
            pdf_filename = f"shipping_label_{order_id}.pdf"
            pdf_path = data_dir / pdf_filename

            # Download the PDF
            response = requests.get(label_url, timeout=30)
            response.raise_for_status()

            # Save to file
            with open(pdf_path, "wb") as f:
                f.write(response.content)

            logger.info("Successfully downloaded label PDF to %s", pdf_path)
            return pdf_path

        except requests.RequestException as e:
            logger.error("Failed to download label PDF for order %s: %s", order_id, e)
        except (OSError, ValueError) as e:
            logger.error(
                "Unexpected error downloading label PDF for order %s: %s", order_id, e
            )

        return None

    def create_test_label_pdf(
        self, order_id: str, tracking_number: str
    ) -> Optional[Path]:
        """
        Create a test PDF label for sandbox testing

        Args:
            order_id: Order identifier
            tracking_number: Mock tracking number

        Returns:
            Path to created test PDF or raises an exception if failed
        """
        # Create data directory if it doesn't exist
        data_dir = Path("data/labels")
        data_dir.mkdir(parents=True, exist_ok=True)

        # Generate filename
        pdf_filename = f"test_shipping_label_{order_id}.pdf"
        pdf_path = data_dir / pdf_filename

        # Create simple test PDF
        c = canvas.Canvas(str(pdf_path), pagesize=landscape(letter))

        # Add test label content
        c.setFont("Helvetica-Bold", 16)
        c.drawString(50, 500, "TEST SHIPPING LABEL")
        c.setFont("Helvetica", 12)
        c.drawString(50, 470, f"Order ID: {order_id}")
        c.drawString(50, 450, f"Tracking Number: {tracking_number}")
        c.drawString(50, 430, "Carrier: USPS Priority Mail")
        c.drawString(50, 410, "*** SANDBOX TEST LABEL ***")
        c.drawString(50, 390, "This is not a real shipping label")

        # Add a border
        c.rect(30, 370, 500, 150, stroke=1, fill=0)

        c.save()

        logger.info("Created test PDF label at %s", pdf_path)
        return pdf_path
