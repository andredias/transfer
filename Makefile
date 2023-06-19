SHELL := /bin/bash -O globstar


run:
	@ docker compose up -d


test:
	pytest -x --cov-report=term-missing --cov-report=html --cov-branch --cov=transfer/

lint:
	@echo
	ruff .
	@echo
	blue --check --diff --color .
	@echo
	mypy .
	@echo
	pip-audit


format:
	ruff --silent --exit-zero --fix .
	blue .


build:
	docker build -t transfer .


run_in_container:
	docker compose up --build
