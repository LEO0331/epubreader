PYTHON ?= python3

.PHONY: install install-dev install-test lint typecheck test coverage run

install:
	$(PYTHON) -m pip install -e .

install-dev:
	$(PYTHON) -m pip install -e .[dev]

install-test:
	$(PYTHON) -m pip install -e .[test]

lint:
	ruff check .

typecheck:
	mypy .

test:
	pytest

coverage:
	pytest --cov=apps --cov=packages --cov-report=term-missing

run:
	uvicorn apps.api.main:create_app --factory --reload --host 127.0.0.1 --port 8000
