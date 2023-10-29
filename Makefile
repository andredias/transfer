SHELL := /usr/bin/env bash -O globstar


run:
	docker compose up --build


test: test_rate_limit unit_test

unit_test:
	pytest -x --cov-report=term-missing --cov-report=html --cov-branch --cov=transfer/


test_rate_limit: build
	trap 'docker compose down' EXIT; \
	docker compose down; docker compose up -d; sleep 5; \
	httpx https://localhost --http2 --no-verify --method POST -f file Makefile; \
	[ $$? -eq 0 ] || exit 1; \
	httpx https://localhost --http2 --no-verify --method POST -f file Makefile; \
	[ $$? -eq 0 ] || exit 2; \
	httpx https://localhost --http2 --no-verify --method POST -f file Makefile; \
	[ $$? -ne 0 ] || exit 3; \
	echo 'Rate limit is working'; exit 0


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
	docker compose build --pull


run_in_container:
	docker compose up --build
