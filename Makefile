.PHONY: install lint format typecheck test run clean

install:
	pip install -e ".[dev]"

lint:
	ruff check app tests

format:
	ruff format app tests

typecheck:
	mypy app

test:
	pytest

run:
	uvicorn app.main:app --reload

clean:
	rm -rf .mypy_cache .pytest_cache .ruff_cache htmlcov .coverage
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
