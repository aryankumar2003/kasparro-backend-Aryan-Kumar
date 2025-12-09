.PHONY: up down test clean

up:
	docker-compose up --build -d

down:
	docker-compose down

test:
	docker-compose run --rm app pytest

clean:
	docker-compose down -v
	find . -type d -name "__pycache__" -exec rm -rf {} +
