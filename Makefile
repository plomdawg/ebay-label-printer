# eBay Label Printer Makefile

.PHONY: help run test lint format build run-container clean install

help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies
	pip install -r requirements.txt

run: ## Run the full automation cycle
	python run.py

test: ## Run all tests
	pytest -v --cov=app tests/

lint: ## Check code style and type hints
	pylint --disable=fixme app/ tests/
	mypy app/ tests/

format: ## Format code with black
	black app/ tests/

format-check: ## Check if code needs formatting
	black --check app/ tests/

build: ## Build the Docker image
	docker build -t ebay-shipper .

run-container: ## Run the container locally
	docker run --env-file .env ebay-shipper

clean: ## Clean up temporary files
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.coverage" -delete
	rm -rf .pytest_cache/
	rm -rf htmlcov/