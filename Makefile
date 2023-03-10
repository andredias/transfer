SHELL := /bin/bash -O globstar

lint:
	cd backend; poetry run make lint


test:
	cd backend; poetry run make test


install_hooks:
	@ scripts/install_hooks.sh
