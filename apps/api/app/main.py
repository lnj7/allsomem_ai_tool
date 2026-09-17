from fastapi import FastAPI

from app.api.routes.auth import router as auth_router
from app.api.routes.health import router as health_router
from app.api.routes.product import router as product_router
from app.core.config import get_settings
from app.core.errors import register_exception_handlers
from app.core.logging import configure_logging
from app.core.middleware import RequestContextMiddleware
from app.core.security import register_security_middleware
from app.db import models as db_models

settings = get_settings()
configure_logging()

app = FastAPI(
    title="Jadon Family creatorOS & co. API",
    version=settings.app_version,
    docs_url="/docs" if not settings.is_production else None,
    redoc_url=None,
)

app.add_middleware(RequestContextMiddleware, settings=settings)
register_security_middleware(app, settings)
register_exception_handlers(app, settings)
app.include_router(health_router)
app.include_router(auth_router)
app.include_router(product_router)

_ = db_models
