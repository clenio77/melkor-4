.DEFAULT_GOAL := help

PYTHON := python
PIP := pip
BACKEND_DIR := kermartin_backend
FRONTEND_DIR := product/frontend
DJANGO_SETTINGS := kermartin_backend.kermartin_project.settings

## ------- Setup -------
.PHONY: setup setup-backend setup-frontend pre-commit-install
setup: setup-backend setup-frontend ## Install backend and frontend deps

setup-backend: ## Install backend deps
	$(PYTHON) -m pip install --upgrade pip
	$(PIP) install -r requirements.txt

setup-frontend: ## Install frontend deps
	cd $(FRONTEND_DIR) && npm ci

pre-commit-install: ## Install pre-commit hooks
	$(PIP) install pre-commit
	pre-commit install

## ------- Lint / Format -------
.PHONY: lint lint-backend lint-frontend format format-backend
lint: lint-backend lint-frontend ## Run all linters

lint-backend: ## flake8 + black --check + isort --check-only
	flake8
	black --check .
	isort --check-only .

lint-frontend: ## ESLint
	cd $(FRONTEND_DIR) && npm run -s lint

format: format-backend ## Apply formatters (black + isort)

format-backend:
	black .
	isort .

## ------- Tests / Build -------
.PHONY: test test-backend build-frontend

test: test-backend ## Run backend tests

test-backend:
	DJANGO_SETTINGS_MODULE=$(DJANGO_SETTINGS) PYTHONPATH=. pytest -q

build-frontend: ## Build Next.js
	cd $(FRONTEND_DIR) && npm run -s build

## ------- Dev -------
.PHONY: dev dev-backend dev-frontend

dev: ## Start both backend and frontend (manual)
	@echo "Run 'make dev-backend' and 'make dev-frontend' in separate terminals."

dev-backend: ## Run Django dev server
	cd $(BACKEND_DIR) && DJANGO_SETTINGS_MODULE=$(DJANGO_SETTINGS) $(PYTHON) manage.py runserver

dev-frontend: ## Run Next.js dev server
	cd $(FRONTEND_DIR) && npm run -s dev

## ------- Help -------
.PHONY: help
help:
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'
