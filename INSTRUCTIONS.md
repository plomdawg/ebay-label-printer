# 📦 Project Brief: eBay Order → Shipping Label & Packing Slip Automation

## 🎯 Objective

Automate the eBay order fulfillment pipeline:

* Detect new orders from eBay.
* Automatically buy shipping labels for them.
* Print both the label and a packing slip to a remote CUPS printer.

---

## 📐 System Overview

### 🔄 Workflow Summary

```
eBay Order Placed → Poll API → Buy Label → Generate Packing Slip → Print Both
```

### 🧱 Architecture

* **Single Docker container** using Python.
* Modular internal components:

  * `orders`: Detect new eBay orders.
  * `labels`: Handle label purchase + refund if needed.
  * `packing`: Generate a packing slip.
  * `print`: Send PDFs to CUPS printer.
* **Test-first development** with Pytest.
* **CI/CD** via GitHub Actions.
* **Task orchestration** via `Makefile` or Bash scripts.

---

## 🔧 Environment

* **Language**: Python 3.11+
* **Containerization**: Docker (single container for all logic)
* **Printing**: Production CUPS server at `localhost`
* **OS**: Ubuntu (host)
* **CI**: GitHub Actions (unit + integration tests)

---

## 📁 Repo Structure

```
ebay-shipper/
├── app/
│   ├── __init__.py
│   ├── orders.py            # eBay API order polling
│   ├── labels.py            # Shipping label buying/refunding
│   ├── packing.py           # Packing slip generation
│   ├── print.py             # Print to CUPS server
│   └── config.py            # eBay tokens, printer IP, etc.
├── tests/
│   ├── test_orders.py
│   ├── test_labels.py
│   ├── test_packing.py
│   └── test_print.py
├── Dockerfile
├── Makefile
├── .github/
│   └── workflows/
│       └── ci.yml           # Run pytest + lint on PRs
├── requirements.txt
└── run.sh                   # Entrypoint logic
```

---

## ⚙️ Functional Requirements

### 1. eBay Order Fetching (`orders.py`)

* Poll eBay Sell API for new orders every few minutes.
* Use the [eBay Order API](https://developer.ebay.com/api-docs/sell/orders/resources/order/methods/getOrder).
* For now, assume a single SKU and static shipping specs.
* Store state (e.g., `seen_order_ids.json`) to avoid duplicates.

### 2. Buy Shipping Label (`labels.py`)

* Use the [eBay Fulfillment API](https://developer.ebay.com/api-docs/sell/fulfillment/resources/shipping_fulfillment/methods/createShippingFulfillment).
* Use static:

  * weight
  * dimensions
  * service (e.g., USPS Priority)
* Download shipping label as PDF.

### 3. Generate Packing List (`packing.py`)

* Generate a 1-page PDF:

  * eBay order ID
  * Quantity
  * Shipping address
  
* Use `reportlab` or `WeasyPrint` for PDF generation.


### 4. Print (`print.py`)

* Send both PDFs (label + packing slip) to the CUPS printer at `localhost`.
* Use Python subprocess to run `lp` or `lpr` commands.
* Allow dry-run mode for tests.

---

## 🔐 Configuration

Use environment variables or `.env` file for:

* `EBAY_CLIENT_ID`, `EBAY_CLIENT_SECRET`, `EBAY_DEV_ID`
* `CUPS_SERVER_URI`
* `PRINTER_NAME`

Store shared configs in `config.py`.

---

## 🧪 Testing Strategy

* Use `pytest` for unit tests and integration tests.
* Mock external APIs (eBay, CUPS) using `pytest-mock` or `unittest.mock`.
* Include tests for:

  * New order detection
  * Label purchase logic
  * PDF generation validity
  * Printing command generation

---

## ⚙️ Makefile Tasks

```makefile
run:  ## Run the full automation cycle
	python run.py

test:  ## Run all tests
	pytest -v

lint:  ## Check code style
	pylint app/ tests/

build:  ## Build the Docker image
	docker build -t ebay-shipper .

run-container:  ## Run the container locally
	docker run --env-file .env ebay-shipper
```

---

## 🧪 GitHub Actions: `.github/workflows/ci.yml`

```yaml
name: CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - run: make lint
      - run: make test
```

---

## 🚧 Future Improvements

* [ ] Add notification approval step (Home Assistant or Discord)
* [ ] Dynamic shipping calculations (per item or buyer location)
* [ ] Web dashboard for logs and order history

---

## ✅ Deliverables

* Dockerized Python app with:

  * Order polling
  * Label purchasing
  * Packing slip generation
  * Auto-printing
* CI pipeline on GitHub
* Full unit test coverage for all modules
* Configuration via `.env` or environment variables
* Minimal dependencies, fast startup, robust logging

---
