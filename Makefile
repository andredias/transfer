SHELL := /bin/bash -O globstar


run:
	@ docker compose up -d redis; \
	ENV=development hypercorn --reload --config=hypercorn.toml 'transfer.main:app'


test:
	@ docker compose up -d redis;
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
