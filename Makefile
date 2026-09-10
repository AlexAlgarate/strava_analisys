.PHONY: help setup run lint format test architecture audit check clean

UV_RUN := uv run --no-sync


help:
	@echo "Available commands:"
	@echo "  make setup        - Install the locked development environment"
	@echo "  make run          - Run the CLI"
	@echo "  make lint         - Check lint, formatting, and types"
	@echo "  make format       - Fix lint issues and format the project"
	@echo "  make test         - Run tests with branch coverage"
	@echo "  make architecture - Check dependency boundaries"
	@echo "  make audit        - Audit locked dependencies for vulnerabilities"
	@echo "  make check        - Run every local CI quality gate"
	@echo "  make clean        - Remove Python cache files"


setup:
	uv sync --locked --all-groups


run:
	$(UV_RUN) python main.py


lint:
	$(UV_RUN) ruff check .
	$(UV_RUN) ruff format --check .
	$(UV_RUN) ty check

format:
	uv run ruff check . --fix
	uv run ruff format .

test:
	$(UV_RUN) pytest tests/ --cov=src --cov=main --cov-report=term-missing

architecture:
	$(UV_RUN) lint-imports --no-cache


audit:
	uv audit --locked --preview-features audit-command


check: lint test architecture audit


clean:
	find . -type d -name "__pycache__" -exec rm -r {} +

	find . -type f -name "*.pyc" -delete
