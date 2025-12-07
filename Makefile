.PHONY: help api frontend run install

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Install dependencies using Poetry
	poetry install

api: ## Run the FastAPI backend server
	poetry run python sds_digest/run_api.py

frontend: ## Run the Streamlit frontend application
	poetry run python sds_digest/run_frontend.py

run: ## Run both API and frontend concurrently
	@echo "Starting API and Frontend..."
	@poetry run python sds_digest/run_api.py & \
	poetry run python sds_digest/run_frontend.py & \
	wait

