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

## Architecture

- **Orders**: Poll eBay API for new orders
- **Labels**: Purchase shipping labels via eBay Fulfillment API  
- **Packing**: Generate QR-coded packing slips as PDFs
- **Print**: Send PDFs to CUPS server
