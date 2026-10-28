.PHONY: help install run migrate seed test lint docker-up docker-down

help:
	@echo "GharSaathi Maths Backend Commands:"
	@echo "  make install     - Install dependencies using uv"
	@echo "  make run         - Run FastAPI backend development server"
	@echo "  make migrate     - Run database migrations"
	@echo "  make seed        - Seed Grade 1-6 mathematics activities"
	@echo "  make test        - Run test suite"
	@echo "  make lint        - Run ruff linter and formatter"
	@echo "  make docker-up   - Start PostgreSQL and FastAPI using Docker Compose"
	@echo "  make docker-down - Stop Docker Compose containers"

install:
	cd backend && uv venv --python 3.12 .venv && uv pip install -e ".[dev]"

run:
	cd backend && uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

migrate:
	cd backend && uv run alembic upgrade head

seed:
	cd backend && uv run python scripts/seed_activities.py

test:
	cd backend && uv run pytest -v

lint:
	cd backend && uv run ruff check . && uv run ruff format --check .

docker-up:
	docker compose up -d --build

docker-down:
	docker compose down
