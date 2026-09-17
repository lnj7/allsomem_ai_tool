SHELL := /bin/bash
COMPOSE := docker compose
API_DIR := apps/api
WEB_DIR := apps/web

.PHONY: help dev up down logs migrate migration test lint format typecheck build env

help:
	@echo "CreatorOS local commands"
	@echo "  make env         Copy .env.example to .env if missing"
	@echo "  make dev         Build and start the full Docker stack"
	@echo "  make up          Start existing Docker services"
	@echo "  make down        Stop Docker services"
	@echo "  make logs        Follow Docker logs"
	@echo "  make migrate     Run Alembic migrations in the API container"
	@echo "  make migration   Create a new Alembic revision (NAME=...)"
	@echo "  make test        Run backend and frontend tests"
	@echo "  make lint        Run Ruff and ESLint"
	@echo "  make format      Run Ruff format and Prettier"
	@echo "  make typecheck   Run mypy and tsc"
	@echo "  make build       Production-build the Next.js app"

env:
	@test -f .env || cp .env.example .env

dev: env
	$(COMPOSE) up --build

up: env
	$(COMPOSE) up -d --build

down:
	$(COMPOSE) down

logs:
	$(COMPOSE) logs -f

migrate:
	$(COMPOSE) exec api alembic upgrade head

migration:
	$(COMPOSE) exec api alembic revision --autogenerate -m "$(NAME)"

test:
	cd $(API_DIR) && .venv/bin/pytest
	cd $(WEB_DIR) && npm test

lint:
	cd $(API_DIR) && .venv/bin/ruff check app tests
	cd $(WEB_DIR) && npm run lint

format:
	cd $(API_DIR) && .venv/bin/ruff format app tests
	cd $(WEB_DIR) && npm run format

typecheck:
	cd $(API_DIR) && .venv/bin/mypy app
	cd $(WEB_DIR) && npm run typecheck

build:
	cd $(WEB_DIR) && npm run build
