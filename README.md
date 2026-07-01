# DevOps Monitoring Dashboard

Python monitoring project with a FastAPI backend and a Streamlit dashboard.
The API exposes system metrics, server CRUD endpoints, manual health checks, and
a WebSocket metrics stream. The dashboard displays live KPIs and registered
servers.

## Architecture

- `api`: FastAPI service on port `8000`
- `dashboard`: Streamlit service on port `8501`
- `docker-compose.yml`: local two-service stack
- `tests`: pytest suite with coverage

## Prerequisites

- Python 3.11
- Docker and Docker Compose
- Make

## Local Run With Docker

```bash
cp .env.example .env
make up
```

Open:

- API docs: <http://localhost:8000/docs>
- Dashboard: <http://localhost:8501>

Stop the stack:

```bash
make down
```

## Local Development

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
make dev
```

## Tests

```bash
make test
make lint
```

## Environment Variables

| Variable | Description |
| --- | --- |
| `API_KEY` | Secret value required for protected server write routes. |
| `API_BASE_URL` | API URL used by the dashboard. In Docker, use `http://api:8000`. |

## API Endpoints

- `GET /health`
- `GET /metrics`
- `WS /ws/metrics`
- `POST /servers` with `X-API-Key`
- `GET /servers`
- `GET /servers/{server_id}`
- `DELETE /servers/{server_id}` with `X-API-Key`
- `POST /servers/{server_id}/check`

## Notes

This submission is configured for local Docker execution. Azure deployment is
not required for this version.
