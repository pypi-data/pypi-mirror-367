#===================== Notes ============================
## To source venv:
## >> source ./.venv/bin/activate


#===================== Categories =======================
.phony: all install venv_create test


#===================== Variables ========================


#===================== Recipes ==========================
all:

install:
	pip install -e .

venv_create:
	pyenv local 3.12
	python -m venv .venv

test:
	python -m unittest discover tests/
