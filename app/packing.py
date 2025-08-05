"""
Packing slip generation

Handles:
- PDF generation for packing slips
- QR code creation linking to orders
- Layout and formatting
"""
# pylint: disable=useless-return

import base64
import binascii
import io
import logging
from typing import Dict, Any, Optional
from pathlib import Path

import qrcode  # type: ignore
from qrcode.image.pil import PilImage  # type: ignore
import reportlab.platypus  # type: ignore
import reportlab.lib.pagesizes  # type: ignore
import reportlab.lib.styles  # type: ignore
import reportlab.lib.colors  # type: ignore
import reportlab.lib.units  # type: ignore

from .config import Config

logger = logging.getLogger(__name__)


class PackingSlipGenerator:
    """Generates packing slips with QR codes"""

    def __init__(self, config: Config):
        self.config = config

    def generate_packing_slip(self, order_data: Dict[str, Any]) -> Optional[Path]:
        """
        Generate a packing slip PDF for the given order

        Args:
            order_data: eBay order information

        Returns:
            Path to generated PDF file, or None if failed
        """
        order_id = order_data.get("order_id", "unknown")
        logger.info("Generating packing slip for order %s", order_id)

        try:
            # Validate order data
            if not self.validate_order_data(order_data):
                logger.error("Invalid order data for order %s", order_id)
                return None

            # Create PDF file path
            output_dir = Path("data/packing_slips")
            output_dir.mkdir(parents=True, exist_ok=True)
            pdf_path = output_dir / f"packing_slip_{order_id}.pdf"

            # Create PDF document
            doc = reportlab.platypus.SimpleDocTemplate(
                str(pdf_path), pagesize=reportlab.lib.pagesizes.letter
            )
            story = self._build_pdf_content(order_data, order_id)

            # Build PDF
            doc.build(story)

            logger.info("Successfully generated packing slip PDF: %s", pdf_path)
            return pdf_path

        except (IOError, OSError) as e:
            logger.error(
                "File system error generating packing slip for order %s: %s",
                order_id,
                str(e),
            )
            return None
        except Exception as e:  # pylint: disable=broad-exception-caught
            logger.error(
                "Failed to generate packing slip for order %s: %s", order_id, str(e)
            )
            return None

    def _build_pdf_content(self, order_data: Dict[str, Any], order_id: str) -> list:
        """
        Build the PDF content for the packing slip

        Args:
            order_data: eBay order information
            order_id: Order identifier

        Returns:
            List of reportlab story elements
        """
        story = []
        styles = reportlab.lib.styles.getSampleStyleSheet()

        # Get custom styles
        title_style, header_style = self._get_pdf_styles(styles)

        # Add title
        story.append(reportlab.platypus.Paragraph("PACKING SLIP", title_style))
        story.append(reportlab.platypus.Spacer(1, 20))

        # Add order information
        story.append(
            reportlab.platypus.Paragraph(f"Order ID: {order_id}", header_style)
        )
        story.append(reportlab.platypus.Spacer(1, 12))

        # Add shipping address
        self._add_shipping_address(story, order_data, header_style, styles)

        # Add items
        self._add_items_list(story, order_data, header_style, styles)

        # Add QR code
        self._add_qr_code(story, order_id, header_style)

        return story

    def _get_pdf_styles(self, styles):
        """Get custom PDF styles"""
        title_style = reportlab.lib.styles.ParagraphStyle(
            "CustomTitle",
            parent=styles["Heading1"],
            fontSize=24,
            spaceAfter=30,
            textColor=reportlab.lib.colors.black,
            alignment=1,  # Center alignment
        )

        header_style = reportlab.lib.styles.ParagraphStyle(
            "CustomHeader",
            parent=styles["Heading2"],
            fontSize=16,
            spaceAfter=12,
            textColor=reportlab.lib.colors.black,
        )

        return title_style, header_style

    def _add_shipping_address(
        self, story: list, order_data: Dict[str, Any], header_style, styles
    ):
        """Add shipping address to PDF story"""
        buyer_address = order_data.get("buyer_address", {})
        if buyer_address:
            story.append(reportlab.platypus.Paragraph("Ship To:", header_style))
            formatted_address = self._format_address(buyer_address)
            for line in formatted_address.split("\n"):
                if line.strip():
                    story.append(reportlab.platypus.Paragraph(line, styles["Normal"]))
            story.append(reportlab.platypus.Spacer(1, 20))

    def _add_items_list(
        self, story: list, order_data: Dict[str, Any], header_style, styles
    ):
        """Add items list to PDF story"""
        items = order_data.get("items", [])
        if items:
            story.append(reportlab.platypus.Paragraph("Items:", header_style))
            for item in items:
                title = item.get("title", "Unknown Item")
                quantity = item.get("quantity", 1)
                item_text = f"• {title} (Qty: {quantity})"
                story.append(reportlab.platypus.Paragraph(item_text, styles["Normal"]))
            story.append(reportlab.platypus.Spacer(1, 20))

    def _add_qr_code(self, story: list, order_id: str, header_style):
        """Add QR code to PDF story"""
        qr_code_base64 = self._generate_qr_code(order_id)
        if qr_code_base64:
            try:
                # Decode base64 and create image
                qr_image_data = base64.b64decode(qr_code_base64)
                qr_buffer = io.BytesIO(qr_image_data)

                # Add QR code to PDF
                story.append(
                    reportlab.platypus.Paragraph("Order QR Code:", header_style)
                )
                story.append(reportlab.platypus.Spacer(1, 6))

                # Create reportlab Image from BytesIO
                qr_img = reportlab.platypus.Image(
                    qr_buffer,
                    width=2 * reportlab.lib.units.inch,
                    height=2 * reportlab.lib.units.inch,
                )
                story.append(qr_img)

            except (ValueError, binascii.Error) as e:
                logger.warning(
                    "Invalid QR code data for order %s: %s", order_id, str(e)
                )
            except (IOError, OSError) as e:
                logger.warning(
                    "Failed to add QR code to PDF for order %s: %s", order_id, str(e)
                )

    def _generate_qr_code(self, order_id: str) -> str:
        """
        Generate QR code for the order

        Args:
            order_id: eBay order identifier

        Returns:
            Base64 encoded QR code image
        """
        logger.debug("Generating QR code for order %s", order_id)

        try:
            # Create QR code instance
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )

            # Add order ID as data
            qr.add_data(f"ORDER:{order_id}")
            qr.make(fit=True)

            # Create image
            img = qr.make_image(
                fill_color="black", back_color="white", image_factory=PilImage
            )

            # Convert to base64
            buffer = io.BytesIO()
            img.save(buffer, format="PNG")
            buffer.seek(0)

            # Encode as base64 string
            qr_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

            logger.debug("Successfully generated QR code for order %s", order_id)
            return qr_base64

        except (IOError, OSError) as e:
            logger.error(
                "File operation error generating QR code for order %s: %s",
                order_id,
                str(e),
            )
            return ""
        except (ValueError, TypeError) as e:
            logger.error(
                "Invalid data for QR code generation for order %s: %s", order_id, str(e)
            )
            return ""
        except Exception as e:  # pylint: disable=broad-exception-caught
            logger.error(
                "Unexpected error generating QR code for order %s: %s", order_id, str(e)
            )
            return ""

    def _format_address(self, address_data: Dict[str, Any]) -> str:
        """
        Format shipping address for display

        Args:
            address_data: Address information from eBay order

        Returns:
            Formatted address string
        """
        if not address_data:
            return ""

        # Extract address components with safe defaults
        name = address_data.get("name", "")
        street1 = address_data.get("street1", "")
        street2 = address_data.get("street2", "")
        city = address_data.get("city", "")
        state = address_data.get("state", "")
        postal_code = address_data.get("postal_code", "")
        country = address_data.get("country", "")

        # Build formatted address
        address_lines = []

        if name:
            address_lines.append(name)

        if street1:
            address_lines.append(street1)

        if street2:
            address_lines.append(street2)

        # City, State ZIP format
        city_line_parts = []
        if city:
            city_line_parts.append(city)
        if state:
            city_line_parts.append(state)
        if postal_code:
            city_line_parts.append(postal_code)

        if city_line_parts:
            if len(city_line_parts) == 3:  # city, state, zip
                address_lines.append(
                    f"{city_line_parts[0]}, {city_line_parts[1]} {city_line_parts[2]}"
                )
            else:
                address_lines.append(" ".join(city_line_parts))

        if country and country.upper() != "US":
            address_lines.append(country)

        return "\n".join(address_lines)

    def validate_order_data(self, order_data: Dict[str, Any]) -> bool:
        """Validate that order data contains required fields for packing slip generation"""
        required_fields = ["order_id", "buyer_address"]
        return all(field in order_data for field in required_fields)
