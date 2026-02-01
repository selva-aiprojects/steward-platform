.PHONY: help up down restart logs build ps

help:
	@echo "Available commands:"
	@echo "  make up      - Start the services with docker-compose"
	@echo "  make down    - Stop the services"
	@echo "  make restart - Restart the services"
	@echo "  make build   - Build or rebuild services"
	@echo "  make logs    - View output from containers"
	@echo "  make ps      - List containers"

up:
	docker-compose up -d

down:
	docker-compose down

restart:
	docker-compose restart

build:
	docker-compose build

logs:
	docker-compose logs -f

ps:
	docker-compose ps
