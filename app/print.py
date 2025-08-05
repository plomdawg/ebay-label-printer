"""
CUPS printing functionality

Handles:
- Sending PDFs to CUPS printer
- Print job management
- Dry-run mode for testing
"""

import logging
import subprocess
from typing import List
from pathlib import Path

from .config import Config

logger = logging.getLogger(__name__)


class PrintManager:
    """Manages printing to CUPS server"""

    def __init__(self, config: Config):
        self.config = config

    def print_documents(self, pdf_paths: List[Path]) -> bool:
        """
        Print multiple PDF documents to the CUPS printer

        Args:
            pdf_paths: List of PDF file paths to print

        Returns:
            True if all documents printed successfully, False otherwise
        """
        if self.config.DRY_RUN:
            logger.info("DRY RUN: Would print %d documents", len(pdf_paths))
            for path in pdf_paths:
                logger.info("DRY RUN: Would print %s", path)
            return True

        success = True
        for pdf_path in pdf_paths:
            if not self._print_single_pdf(pdf_path):
                success = False

        return success

    def _print_single_pdf(self, pdf_path: Path) -> bool:
        """
        Print a single PDF to the CUPS printer

        Args:
            pdf_path: Path to PDF file

        Returns:
            True if printed successfully, False otherwise
        """
        if not pdf_path.exists():
            logger.error("PDF file not found: %s", pdf_path)
            return False

        try:
            # Use lp command to print to CUPS server
            cmd = [
                "lp",
                "-h",
                self.config.CUPS_SERVER_URI,
                "-d",
                self.config.PRINTER_NAME,
                str(pdf_path),
            ]

            logger.info("Printing %s to %s", pdf_path, self.config.PRINTER_NAME)
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)

            if result.returncode == 0:
                logger.info("Successfully printed %s", pdf_path)
                return True
            logger.error("Print failed for %s: %s", pdf_path, result.stderr)
            return False

        except subprocess.CalledProcessError as e:
            logger.error("Print command failed for %s: %s", pdf_path, e)
            return False
        except (OSError, FileNotFoundError) as e:
            logger.error("System error printing %s: %s", pdf_path, e)
            return False

    def test_printer_connection(self) -> bool:
        """
        Test connection to CUPS printer

        Returns:
            True if printer is accessible, False otherwise
        """
        try:
            cmd = [
                "lpstat",
                "-h",
                self.config.CUPS_SERVER_URI,
                "-p",
                self.config.PRINTER_NAME,
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)

            if result.returncode == 0:
                logger.info("Printer %s is accessible", self.config.PRINTER_NAME)
                return True
            logger.error("Printer test failed: %s", result.stderr)
            return False

        except subprocess.CalledProcessError as e:
            logger.error("Printer test command failed: %s", e)
            return False
        except (OSError, FileNotFoundError) as e:
            logger.error("System error testing printer: %s", e)
            return False
