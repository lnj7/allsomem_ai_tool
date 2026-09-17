import os

os.environ.setdefault("APP_ENV", "test")
os.environ.setdefault(
    "DATABASE_URL",
    "postgresql+psycopg://creatoros:creatoros@localhost:5432/creatoros",
)
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")
os.environ.setdefault("SECRET_KEY", "test-secret-key")
os.environ.setdefault("FRONTEND_URL", "http://localhost:3000")
# Tests must not spend the developer OpenAI key or skip the unconfigured-provider check.
os.environ["AI_API_KEY"] = ""
