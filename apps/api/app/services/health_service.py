from sqlalchemy import text
from sqlalchemy.orm import Session

from app.integrations.cache.base import CacheClient
from app.schemas.health import HealthLiveResponse, HealthReadyResponse


class HealthService:
    def __init__(self, db: Session, cache: CacheClient) -> None:
        self._db = db
        self._cache = cache

    def liveness(self) -> HealthLiveResponse:
        return HealthLiveResponse(status="ok", service="creatoros-api")

    def readiness(self) -> tuple[HealthReadyResponse, int]:
        database = "ok" if self._check_database() else "unavailable"
        redis_status = "ok" if self._check_redis() else "unavailable"
        ready = database == "ok" and redis_status == "ok"
        payload = HealthReadyResponse(
            status="ready" if ready else "not_ready",
            database=database,
            redis=redis_status,
        )
        return payload, 200 if ready else 503

    def _check_database(self) -> bool:
        try:
            self._db.execute(text("SELECT 1"))
            return True
        except Exception:
            return False

    def _check_redis(self) -> bool:
        return self._cache.ping()
