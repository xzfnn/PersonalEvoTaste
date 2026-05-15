.PHONY: install dev test lint format typecheck demo clean

install:
	python -m pip install -e .

dev:
	python -m pip install -e ".[dev]"

test:
	pytest --cov=personal_evotaste --cov-report=term-missing

lint:
	ruff check personal_evotaste tests

format:
	ruff format personal_evotaste tests

typecheck:
	mypy personal_evotaste

demo:
	python examples/demo.py

clean:
	rm -rf build dist *.egg-info .pytest_cache .mypy_cache .ruff_cache htmlcov .coverage
