# eBay Label Printer

Automates eBay order fulfillment: detects new orders → buys shipping labels → generates packing slips → prints both to CUPS printer.

## Quick Start

```bash
# Install dependencies
make install

# Run the automation
make run

# Run tests
make test

# Format and lint code
make format
make lint
```

## Architecture

- **Orders**: Poll eBay API for new orders
- **Labels**: Purchase shipping labels via eBay Fulfillment API  
- **Packing**: Generate QR-coded packing slips as PDFs
- **Print**: Send PDFs to CUPS server at 192.168.8.194

## Configuration

Set environment variables:
- `EBAY_CLIENT_ID`, `EBAY_CLIENT_SECRET`, `EBAY_REFRESH_TOKEN`
- `CUPS_SERVER_URI`, `PRINTER_NAME`

## Docker

```bash
make build
make run-container
```
