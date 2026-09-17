# Architecture

Milestone 1 uses a layered local stack.

```
Browser
  → Next.js (apps/web)
    → FastAPI (apps/api)
      → PostgreSQL
    FastAPI
      → Redis
```

## Frontend

The web app is a Next.js App Router TypeScript application. It talks to the API through a typed client in `apps/web/lib/api`. Dashboard backend status is a real `GET /health` call. There is no mocked success path.

## Backend

FastAPI routes stay thin. Health checks run through `HealthService`. Redis is accessed through a `CacheClient` interface so the cache implementation can change later.

## Data

SQLAlchemy 2.x manages connections with a process-wide engine and session factory. Alembic owns schema changes.

## Future layers

`app/ai`, `app/workers`, and social adapters are reserved packages. They are not implemented in Milestone 1.
