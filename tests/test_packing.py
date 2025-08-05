"""
Tests for packing slip generation
"""
# pylint: disable=protected-access, attribute-defined-outside-init, assignment-from-none

from unittest.mock import patch

from app.config import Config
from app.packing import PackingSlipGenerator


class TestPackingSlipGenerator:
    """Test packing slip generation functionality"""

    def setup_method(self):
        """Set up test fixtures"""
        self.config = Config()
        self.packing_generator = PackingSlipGenerator(self.config)

    def test_init_creates_generator(self):
        """Test that PackingSlipGenerator initializes correctly"""
        assert self.packing_generator.config == self.config
        assert isinstance(self.packing_generator, PackingSlipGenerator)

    def test_generate_packing_slip_with_valid_order(self):
        """Test generating packing slip with valid order data"""
        order_data = {
            "order_id": "12345-67890",
            "buyer_address": {
                "name": "John Doe",
                "street": "123 Main St",
                "city": "Anytown",
                "state": "CA",
                "postalCode": "12345",
            },
            "quantity": 2,
            "total": "25.00",
        }

        # Should return a Path to the generated PDF
        result = self.packing_generator.generate_packing_slip(order_data)
        assert result is not None
        assert result.name == "packing_slip_12345-67890.pdf"
        assert result.exists()  # File should be created

    def test_generate_packing_slip_with_missing_order_id(self):
        """Test generating packing slip with missing order ID"""
        order_data = {
            "buyer_address": {"name": "John Doe", "street": "123 Main St"},
            "quantity": 1,
        }

        result = self.packing_generator.generate_packing_slip(order_data)
        assert result is None

    def test_generate_packing_slip_with_empty_order(self):
        """Test generating packing slip with empty order data"""
        order_data = {}

        result = self.packing_generator.generate_packing_slip(order_data)
        assert result is None

    def test_generate_qr_code_with_valid_order_id(self):
        """Test generating QR code with valid order ID"""
        order_id = "12345-67890"

        # Should return base64 encoded QR code image
        result = self.packing_generator._generate_qr_code(order_id)
        assert result != ""
        assert isinstance(result, str)
        # Should be valid base64
        import base64
        try:
            base64.b64decode(result)
        except Exception:
            assert False, "Result should be valid base64"

    def test_generate_qr_code_with_empty_order_id(self):
        """Test generating QR code with empty order ID"""
        order_id = ""

        # Should still generate QR code, even with empty order ID
        result = self.packing_generator._generate_qr_code(order_id)
        assert result != ""
        assert isinstance(result, str)

    def test_format_address_with_valid_data(self):
        """Test formatting address with valid address data"""
        address_data = {
            "name": "John Doe",
            "street1": "123 Main St",
            "city": "Anytown",
            "state": "CA",
            "postal_code": "12345",
        }

        # Should return formatted address string
        result = self.packing_generator._format_address(address_data)
        expected = "John Doe\n123 Main St\nAnytown, CA 12345"
        assert result == expected

    def test_format_address_with_empty_data(self):
        """Test formatting address with empty address data"""
        address_data = {}

        result = self.packing_generator._format_address(address_data)
        assert result == ""

    def test_validate_order_data_with_complete_data(self):
        """Test validating order data with all required fields"""
        order_data = {
            "order_id": "12345-67890",
            "buyer_address": {"name": "John Doe", "street": "123 Main St"},
        }

        result = self.packing_generator.validate_order_data(order_data)
        assert result is True

    def test_validate_order_data_missing_order_id(self):
        """Test validating order data missing order_id"""
        order_data = {"buyer_address": {"name": "John Doe", "street": "123 Main St"}}

        result = self.packing_generator.validate_order_data(order_data)
        assert result is False

    def test_validate_order_data_missing_buyer_address(self):
        """Test validating order data missing buyer_address"""
        order_data = {"order_id": "12345-67890"}

        result = self.packing_generator.validate_order_data(order_data)
        assert result is False

    def test_validate_order_data_empty_data(self):
        """Test validating empty order data"""
        order_data = {}

        result = self.packing_generator.validate_order_data(order_data)
        assert result is False

    @patch("app.packing.logger")
    def test_generate_packing_slip_logs_correctly(self, mock_logger):
        """Test that generate_packing_slip logs the correct information"""
        order_data = {"order_id": "12345-67890"}

        self.packing_generator.generate_packing_slip(order_data)

        mock_logger.info.assert_called_once_with(
            "Generating packing slip for order %s", "12345-67890"
        )

    @patch("app.packing.logger")
    def test_generate_packing_slip_logs_unknown_order(self, mock_logger):
        """Test that generate_packing_slip logs 'unknown' for missing order_id"""
        order_data = {}

        self.packing_generator.generate_packing_slip(order_data)

        mock_logger.info.assert_called_once_with(
            "Generating packing slip for order %s", "unknown"
        )

    @patch("app.packing.logger")
    def test_generate_qr_code_logs_debug(self, mock_logger):
        """Test that _generate_qr_code logs debug information"""
        order_id = "12345-67890"

        self.packing_generator._generate_qr_code(order_id)

        # Should call debug twice: once at start, once on success
        assert mock_logger.debug.call_count == 2
        mock_logger.debug.assert_any_call(
            "Generating QR code for order %s", "12345-67890"
        )
        mock_logger.debug.assert_any_call(
            "Successfully generated QR code for order %s", "12345-67890"
        )

    def test_config_dependency(self):
        """Test that PackingSlipGenerator properly uses the config object"""
        # Test that the generator stores and can access config
        assert hasattr(self.packing_generator, "config")
        assert self.packing_generator.config is not None

    def test_multiple_packing_operations(self):
        """Test performing multiple packing operations in sequence"""
        order_data = {"order_id": "12345-67890", "buyer_address": {"name": "John Doe"}}

        # Should be able to perform multiple operations
        result1 = self.packing_generator.generate_packing_slip(order_data)
        result2 = self.packing_generator._generate_qr_code("12345-67890")
        result3 = self.packing_generator.validate_order_data(order_data)

        assert result1 is not None  # Should return Path to PDF
        assert result2 != ""  # Should return base64 QR code
        assert result3 is True  # Should validate successfully

    def test_required_fields_validation(self):
        """Test that validate_order_data checks the correct required fields"""
        # Test with partial data for each required field
        test_cases = [
            ({"order_id": "123"}, False),  # Missing buyer_address
            ({"buyer_address": {}}, False),  # Missing order_id
            ({"order_id": "123", "buyer_address": {}}, True),  # Both present
            (
                {"order_id": "123", "buyer_address": {}, "extra_field": "value"},
                True,
            ),  # Extra fields OK
        ]

        for order_data, expected in test_cases:
            result = self.packing_generator.validate_order_data(order_data)
            assert result == expected, f"Failed for order_data: {order_data}"
