.PHONY: build check lint test typecheck

PYTHON ?= python3

test:
	$(PYTHON) -m pytest

lint:
	$(PYTHON) -m ruff check .

typecheck:
	$(PYTHON) -m mypy

check: lint typecheck test

build:
	$(PYTHON) -m build
