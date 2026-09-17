from app.services.health_service import HealthService


class FakeResult:
    pass


class FakeDb:
    def __init__(self, fail: bool = False) -> None:
        self.fail = fail

    def execute(self, _statement):  # noqa: ANN001
        if self.fail:
            raise RuntimeError("database unavailable")
        return FakeResult()


class FakeCache:
    def __init__(self, ok: bool = True) -> None:
        self.ok = ok

    def ping(self) -> bool:
        return self.ok

    def close(self) -> None:
        return None


def test_liveness() -> None:
    service = HealthService(db=FakeDb(), cache=FakeCache())
    result = service.liveness()
    assert result.status == "ok"
    assert result.service == "creatoros-api"


def test_ready_when_dependencies_ok() -> None:
    service = HealthService(db=FakeDb(), cache=FakeCache())
    payload, status = service.readiness()
    assert status == 200
    assert payload.status == "ready"
    assert payload.database == "ok"
    assert payload.redis == "ok"


def test_ready_when_database_unavailable() -> None:
    service = HealthService(db=FakeDb(fail=True), cache=FakeCache())
    payload, status = service.readiness()
    assert status == 503
    assert payload.status == "not_ready"
    assert payload.database == "unavailable"
    assert payload.redis == "ok"


def test_ready_when_redis_unavailable() -> None:
    service = HealthService(db=FakeDb(), cache=FakeCache(ok=False))
    payload, status = service.readiness()
    assert status == 503
    assert payload.status == "not_ready"
    assert payload.redis == "unavailable"
