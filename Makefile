.PHONY: up down logs test lint dev api dashboard

up:
	docker compose up --build -d

down:
	docker compose down -v

logs:
	docker compose logs -f

test:
	pytest tests/ -v --cov=api --cov-fail-under=75

lint:
	flake8 api/ dashboard/ tests/

dev:
	$(MAKE) -j2 api dashboard

api:
	uvicorn api.main:app --reload --port 8000

dashboard:
	API_BASE_URL=http://localhost:8000 streamlit run dashboard/app.py
