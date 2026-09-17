# Database

PostgreSQL 16 is the system of record.

Local Docker credentials (development only):

- database: `creatoros`
- user: `creatoros`
- password: `creatoros`

## users

| Column | Type | Notes |
| --- | --- | --- |
| id | UUID | Primary key |
| email | VARCHAR(320) | Unique, indexed, not null |
| password_hash | VARCHAR(255) | Nullable until authentication is implemented |
| full_name | VARCHAR(200) | Not null |
| is_active | BOOLEAN | Default true |
| created_at | TIMESTAMPTZ | Server default now() |
| updated_at | TIMESTAMPTZ | Server default now() |

Migration: `apps/api/alembic/versions/0001_create_users.py`

Apply with `alembic upgrade head`.
