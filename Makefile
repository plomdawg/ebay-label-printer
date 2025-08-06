# eBay Label Printer Makefile

.PHONY: help test test-print test-api-sandbox test-api-production test-api-all lint format build run-container clean install

help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies
	pip install -r requirements.txt

test: ## Run all tests
	pytest -v --cov=app tests/

test-print: ## Run print tests
	pytest -v --cov=app tests/ -m print

test-api-sandbox: ## Run eBay sandbox API tests (requires sandbox credentials)
	pytest -v --cov=app tests/ -m api_sandbox -s

test-api-production: ## Run eBay production API tests (requires production credentials)
	pytest -v --cov=app tests/ -m api_production -s

test-api-all: ## Run all eBay API tests (both sandbox and production)
	pytest -v --cov=app tests/ -m "api_sandbox or api_production" -s

lint: ## Check code style and type hints
	pylint --disable=fixme app/ tests/
	mypy app/ tests/

format: ## Format code with black
	black app/ tests/

format-check: ## Check if code needs formatting
	black --check app/ tests/

build: ## Build the Docker image
	docker build -t ebay-shipper .

run: ## Run the container
	docker run --env-file .env ebay-shipper

clean: ## Clean up temporary files
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.coverage" -delete
	rm -rf .pytest_cache/
	rm -rf htmlcov/