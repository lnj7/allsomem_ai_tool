from collections.abc import Generator

from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.integrations.cache import get_cache_client
from app.integrations.cache.base import CacheClient
from app.services.health_service import HealthService


def get_health_service(
    db: Session = Depends(get_db),
    cache: CacheClient = Depends(get_cache_client),
) -> Generator[HealthService, None, None]:
    yield HealthService(db=db, cache=cache)
