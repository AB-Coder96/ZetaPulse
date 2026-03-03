SHELL := /bin/bash

.PHONY: up down logs api worker web fmt lint test

up:
	docker compose up -d --build

down:
	docker compose down -v

logs:
	docker compose logs -f --tail=200

api:
	docker compose up -d --build backend

worker:
	docker compose up -d --build worker

web:
	docker compose up -d --build frontend

fmt:
	docker compose exec backend ruff format .

lint:
	docker compose exec backend ruff check .
	docker compose exec backend pytest -q

test:
	docker compose exec backend pytest -q
