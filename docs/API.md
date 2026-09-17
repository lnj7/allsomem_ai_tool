# API

Base URL in local development: `http://localhost:8000`

Future product APIs will live under `/api/v1/`. Health endpoints stay at the root so load balancers can probe them without version coupling.

## GET /health

Liveness. Confirms the API process is running.

```json
{
  "status": "ok",
  "service": "creatoros-api"
}
```

Status: `200`

## GET /health/ready

Readiness. Checks PostgreSQL and Redis.

Ready:

```json
{
  "status": "ready",
  "database": "ok",
  "redis": "ok"
}
```

Status: `200`

Not ready:

```json
{
  "status": "not_ready",
  "database": "unavailable",
  "redis": "ok"
}
```

Status: `503`

Error envelope for unexpected failures:

```json
{
  "error": {
    "code": "INTERNAL_ERROR",
    "message": "An unexpected error occurred.",
    "request_id": "..."
  }
}
```
