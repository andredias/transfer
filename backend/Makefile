SHELL := /bin/bash -O globstar


run:
	hypercorn --reload --config=hypercorn.toml 'transfer.main:app'


test:
	pytest -x --cov-report term-missing --cov-report html --cov-branch \
	       --cov transfer/


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


smoke_test: build
	docker run --rm -d -p 5000:5000 --name transfer transfer
	sleep 2; curl http://localhost:5000/hello
	docker stop transfer
