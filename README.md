# eBay Label Printer

Automates eBay order fulfillment: detects new orders → buys shipping labels → generates packing slips → prints both to CUPS printer.

## Quick Start

Set environment variables:
- `EBAY_CLIENT_ID`, `EBAY_CLIENT_SECRET`, `EBAY_REFRESH_TOKEN`
- `CUPS_SERVER_URI`, `PRINTER_NAME`

```bash
# Format and lint code
make format lint

# Run tests
make test

# Run the container
make build
make run
```

## Hardware Testing

Tests that interact with actual printers are available but **skipped by default**. The `test_actual_printer_hardware` test generates and prints a real packing slip for order "TEST-001".

**Run hardware tests:**
```bash
pytest -m print
```

**Prerequisites:**
- Printer connected and ready (`lpstat -p` to check status)
- CUPS running (`sudo systemctl status cups`)
- Paper/labels loaded
- Correct `CUPS_SERVER_URI` and `PRINTER_NAME` in config

⚠️ **Warning:** Hardware tests will actually print pages!

## Architecture

- **Orders**: Poll eBay API for new orders
- **Labels**: Purchase shipping labels via eBay Fulfillment API  
- **Packing**: Generate QR-coded packing slips as PDFs
- **Print**: Send PDFs to CUPS server
