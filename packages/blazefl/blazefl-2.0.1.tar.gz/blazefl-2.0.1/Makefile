format:
	ruff format .

lint:
	ruff check . --fix
	mypy src

test:
	pytest -v tests

stubgen:
	stubgen -p blazefl.core -p blazefl.reproducibility --no-analysis -o src
