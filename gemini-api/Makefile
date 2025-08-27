APP = app:app
PORT = 8000

.PHONY: run up up-d down format lint install

run:
	uvicorn $(APP) --reload --host 0.0.0.0 --port $(PORT)

up:
	docker compose up --build

up-d:
	docker compose up -d --build

down:
	docker compose down

format:
	black .
	isort .

lint:
	flake8 .
	mypy .

install:
	pip install -r requirements-dev.txt
