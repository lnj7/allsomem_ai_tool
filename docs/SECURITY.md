# Security

Milestone 1 baseline:

- Secrets come from environment variables. `.env` is gitignored.
- `SECRET_KEY` is required. The committed `.env.example` value is a placeholder.
- CORS origins are explicit (`FRONTEND_URL` plus optional `CORS_ORIGINS`). Wildcard origins are not used.
- Request bodies over `REQUEST_MAX_BYTES` (default 1MB) are rejected.
- Structured logs include request IDs. Passwords, tokens, and API keys must not be logged.
- `password_hash` exists on `users` but is never exposed by an API in this milestone.
- Production should disable `/docs` (controlled by `APP_ENV`).

Authentication, OAuth, and social tokens are not implemented yet.
