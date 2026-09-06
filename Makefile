map = maps/challenger/01_the_impossible_dream.txt

install:
	pip3 install flake8 mypy

run:
	@python3 -m src --map "$(map)"

debug:
	@python3 -m pdb -m src

lint:
	@flake8 src/
	@mypy src/ --follow-imports=skip --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

clean:
	@rm -rf .mypy_cache
	@rm -rf .pytest_cache
	@rm -rf .venv
	@rm -rf .vscode
	@find . -type d -name "__pycache__" -exec rm -rf {} +
	@find . -type f -name "*.pyc" -delete
	@find . -type f -name "*.pyo" -delete

.PHONY: install run debug clean lint