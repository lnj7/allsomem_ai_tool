# CreatorOS

CreatorOS is an AI-powered Creator Operating System. Milestone 1 delivers the local foundation: a Next.js application shell, a FastAPI API, PostgreSQL, Redis, health checks, and Docker Compose.

This is **not** a complete product yet. Authentication, AI profile generation, and social publishing are later milestones.

Use [PROCEDURE.md](PROCEDURE.md) for the shortest start/stop/edit steps.

## Architecture

```
Browser → Next.js (apps/web) → FastAPI (apps/api) → PostgreSQL
                                 FastAPI → Redis
```

## Prerequisites

- Docker and Docker Compose (Colima is supported on macOS)
- Node.js 22+ (for host-side frontend tests and builds)
- Python 3.12 (Homebrew `python@3.12`; do not use 3.14 for the API venv)
- Docker / Colima (optional, for `docker compose`)

## Environment setup

```bash
cp .env.example .env
```

Local development database credentials in Docker are `creatoros` / `creatoros`. Do not use them in production.

## Docker startup

```bash
docker compose up --build
```

Or:

```bash
make dev
```

Then open:

- Frontend: http://localhost:3000
- Dashboard: http://localhost:3000/dashboard
- API liveness: http://localhost:8000/health
- API readiness: http://localhost:8000/health/ready

The API container runs `alembic upgrade head` on startup.

## Host-only local run (this machine)

PostgreSQL 16 and Redis are installed via Homebrew and already configured for CreatorOS.

```bash
brew services start postgresql@16
brew services start redis
cd apps/api
source .venv/bin/activate
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

In another terminal:

```bash
cd apps/web
npm run dev
```

Use Python 3.12 for the API virtualenv (`python3.12 -m venv .venv`). System Python 3.14 cannot install the pinned Pydantic wheels.

If you use Docker Compose, stop the Homebrew database services first so ports 5432 and 6379 are free:

```bash
brew services stop postgresql@16
brew services stop redis
docker compose up --build
```

## Database migrations

```bash
make migrate
# or
docker compose exec api alembic upgrade head
```

Create a new revision:

```bash
make migration NAME="add_example"
```

## Testing

```bash
# Backend unit/API tests
cd apps/api && .venv/bin/pytest

# Live Postgres + Redis readiness
RUN_INTEGRATION=1 cd apps/api && .venv/bin/pytest tests/integration

# Frontend
cd apps/web && npm test
```

## Linting and type checking

```bash
cd apps/api && .venv/bin/ruff check app tests
cd apps/api && .venv/bin/mypy app
cd apps/web && npm run lint
cd apps/web && npm run typecheck
```

## Frontend production build

```bash
cd apps/web && npm run build
```

## AI configuration

`AI_API_KEY` and `AI_MODEL` are reserved for later milestones. Milestone 1 does not call an AI provider.

## Troubleshooting

- **Port already in use:** stop local Postgres/Redis or change Compose ports.
- **Dashboard shows Backend: Unavailable:** confirm http://localhost:8000/health and that the browser can reach it (CORS uses `FRONTEND_URL`).
- **`/health/ready` returns 503:** Postgres or Redis is not healthy yet. Wait for container healthchecks.
- **Docker not found:** install Docker Desktop or `brew install colima docker docker-compose` and run `colima start`.
