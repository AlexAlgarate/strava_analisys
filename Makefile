.PHONY: help run lint format test import-linter clean setup


help:
	@echo "Comandos disponibles:"
	@echo "  make run             - Run main.py"
	@echo "  make lint            - Lint with ruff + mypy"
	@echo "  make format          - Format with ruff"
	@echo "  make test            - Run tests with pytest"
	@echo "  make import-linter   - Check clean architecture with import-linter"
	@echo "  make clean           - Drop temporary files"


run:
	uv run python main.py


lint:
	uv run ruff check src
	uv run mypy src

format:
	uv run ruff format src



test:
	uv run pytest

import-linter:
	uv run lint-imports --no-cache


clean:
	find . -type d -name "__pycache__" -exec rm -r {} +
	find . -type f -name "*.pyc" -delete