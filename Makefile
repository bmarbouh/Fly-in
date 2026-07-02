PYTHON = uv run python3


install:
	uv sync
	uv add flake8

run:
	@$(PYTHON) -m src

debug:
	@$(PYTHON) -m pdb -m src

lint:
	@uv run flake8 src/
	@uv run mypy src/ --follow-imports=skip --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

clean:
	@rm -rf .mypy_cache
	@rm -rf .pytest_cache
	@find . -type d -name "__pycache__" -exec rm -rf {} +
	@find . -type f -name "*.pyc" -delete
	@find . -type f -name "*.pyo" -delete

.PHONY: install run debug clean lint