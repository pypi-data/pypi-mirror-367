PYTHON?=python
SOURCES=feedforward setup.py

UV:=$(shell uv --version)
ifdef UV
	VENV:=uv venv
	PIP:=uv pip
else
	VENV:=python -m venv
	PIP:=python -m pip
endif

.PHONY: venv
venv:
	$(VENV) .venv
	source .venv/bin/activate && make setup
	@echo 'run `source .venv/bin/activate` to use virtualenv'

# The rest of these are intended to be run within the venv, where python points
# to whatever was used to set up the venv.

.PHONY: setup
setup:
	$(PIP) install -Ue .[dev,test]

.PHONY: test
test:
	pytest --cov=feedforward --cov=tests --cov-report= $(TESTOPTS)
	python -m coverage report

.PHONY: html
html: .venv README.md docs/*.rst docs/conf.py
	source .venv/bin/activate && sphinx-build -ab html docs html

.PHONY: format
format:
	ruff format
	ruff check --fix

.PHONY: lint
lint:
	ruff check $(SOURCES)
	python -m checkdeps --allow-names feedforward feedforward
	mypy --strict --install-types --non-interactive feedforward

.PHONY: release
release:
	rm -rf dist
	python setup.py sdist bdist_wheel
	twine upload dist/*
