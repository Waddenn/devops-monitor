# DevOps Monitoring Dashboard

Mini-projet Python avec une API FastAPI et un dashboard Streamlit.

- API : métriques système, CRUD serveurs, health checks, WebSocket
- Dashboard : KPIs live, graphique, tableau des serveurs
- Docker Compose : API + dashboard en local
- CI GitHub : lint, tests, build Docker, publication GHCR

## Lancer Le Projet

```bash
cp .env.example .env
make up
```

- API docs : http://localhost:8000/docs
- Dashboard : http://localhost:8501

Arrêter :

```bash
make down
```

## Développement

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
make dev
```

## Tests

```bash
make lint
make test
```

## Endpoints Principaux

- `GET /health`
- `GET /metrics`
- `WS /ws/metrics`
- `POST /servers` avec `X-API-Key`
- `GET /servers`
- `DELETE /servers/{server_id}` avec `X-API-Key`
- `POST /servers/{server_id}/check`

## Images Docker

```bash
docker pull ghcr.io/waddenn/devops-monitor-api:latest
docker pull ghcr.io/waddenn/devops-monitor-dashboard:latest
```

## Variables

- `API_KEY` : clé utilisée pour les routes protégées
- `API_BASE_URL` : URL de l'API utilisée par le dashboard

Azure n'est pas requis pour cette version.
