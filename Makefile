.PHONY: help install test lint build up down clean

help:
	@echo "CoworkFlow - Makefile Commands"
	@echo "================================"
	@echo "install    - Install dependencies"
	@echo "test       - Run tests"
	@echo "lint       - Run linter"
	@echo "build      - Build Docker images"
	@echo "up         - Start services"
	@echo "down       - Stop services"
	@echo "clean      - Clean containers and images"

install:
	pip install -r ms-usuarios/requirements.txt
	pip install -r api-gateway/requirements.txt
	pip install -r frontend/requirements.txt
	pip install pytest pytest-cov flake8

test:
	pytest tests/ --cov=. --cov-report=html

lint:
	flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
	flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics

build:
	docker-compose build

up:
	docker-compose up -d

down:
	docker-compose down

clean:
	docker-compose down -v
	docker system prune -af