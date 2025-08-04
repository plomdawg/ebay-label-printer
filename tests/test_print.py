"""
Tests for printing functionality
"""

import tempfile
from pathlib import Path
from subprocess import CalledProcessError
from unittest.mock import Mock, patch, MagicMock

from app.print import PrintManager
from app.config import Config


class TestPrintManager:
    """Test CUPS printing functionality"""

    def setup_method(self):
        """Set up test fixtures"""
        self.config = Mock(spec=Config)
        self.config.CUPS_SERVER_URI = "192.168.8.194"
        self.config.PRINTER_NAME = "test_printer"
        self.config.DRY_RUN = False

    def test_init_creates_manager(self):
        """Test that PrintManager initializes correctly"""
        manager = PrintManager(self.config)
        assert manager.config == self.config

    def test_print_documents_dry_run(self):
        """Test dry run mode doesn't actually print"""
        self.config.DRY_RUN = True
        manager = PrintManager(self.config)

        with tempfile.TemporaryDirectory() as tmpdir:
            pdf1 = Path(tmpdir) / "test1.pdf"
            pdf2 = Path(tmpdir) / "test2.pdf"
            pdf1.touch()
            pdf2.touch()

            result = manager.print_documents([pdf1, pdf2])
            assert result is True

    @patch("app.print.subprocess.run")
    def test_print_single_pdf_success(self, mock_run):
        """Test successful printing of a single PDF"""
        mock_run.return_value = MagicMock(returncode=0)
        manager = PrintManager(self.config)

        with tempfile.TemporaryDirectory() as tmpdir:
            pdf_file = Path(tmpdir) / "test.pdf"
            pdf_file.touch()

            result = manager._print_single_pdf(pdf_file)
            assert result is True

            # Verify correct command was called
            mock_run.assert_called_once()
            args = mock_run.call_args[0][0]
            assert args[0] == "lp"
            assert "-h" in args and "192.168.8.194" in args
            assert "-d" in args and "test_printer" in args
            assert str(pdf_file) in args

    def test_print_single_pdf_file_not_found(self):
        """Test printing when PDF file doesn't exist"""
        manager = PrintManager(self.config)

        nonexistent_file = Path("/nonexistent/file.pdf")
        result = manager._print_single_pdf(nonexistent_file)
        assert result is False

    @patch("app.print.subprocess.run")
    def test_print_single_pdf_command_failure(self, mock_run):
        """Test handling of print command failure"""
        mock_run.side_effect = CalledProcessError(1, "lp", stderr="Printer error")

        manager = PrintManager(self.config)

        with tempfile.TemporaryDirectory() as tmpdir:
            pdf_file = Path(tmpdir) / "test.pdf"
            pdf_file.touch()

            result = manager._print_single_pdf(pdf_file)
            assert result is False

    @patch("app.print.subprocess.run")
    def test_test_printer_connection_success(self, mock_run):
        """Test successful printer connection test"""
        mock_run.return_value = MagicMock(returncode=0)
        manager = PrintManager(self.config)

        result = manager.test_printer_connection()
        assert result is True

        # Verify correct command was called
        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        assert args[0] == "lpstat"
        assert "-h" in args and "192.168.8.194" in args
        assert "-p" in args and "test_printer" in args

    @patch("app.print.subprocess.run")
    def test_test_printer_connection_failure(self, mock_run):
        """Test printer connection test failure"""
        mock_run.side_effect = CalledProcessError(
            1, "lpstat", stderr="Printer not found"
        )

        manager = PrintManager(self.config)
        result = manager.test_printer_connection()
        assert result is False
