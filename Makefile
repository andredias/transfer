SHELL := /bin/bash -O globstar


run:
	@ docker compose up -d


test: test_rate_limit
	pytest -x --cov-report=term-missing --cov-report=html --cov-branch --cov=transfer/


test_rate_limit:
	trap 'docker compose down' EXIT; \
	docker compose down; docker compose up -d; sleep 2; \
	https --verify no --check-status --form POST localhost file@./Makefile; \
	[ $$? -eq 0 ] || exit 1; \
	https --verify no --check-status --form POST localhost file@./Makefile; \
	[ $$? -eq 0 ] || exit 2; \
	https --verify no --check-status --form POST localhost file@./Makefile; \
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
	docker build -t transfer .


run_in_container:
	docker compose up --build
