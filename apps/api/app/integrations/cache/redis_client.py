from redis import Redis
from redis.exceptions import RedisError

from app.integrations.cache.base import CacheClient


class RedisCacheClient(CacheClient):
    def __init__(self, url: str, timeout_seconds: float = 2.0) -> None:
        self._client = Redis.from_url(
            url,
            socket_connect_timeout=timeout_seconds,
            socket_timeout=timeout_seconds,
            decode_responses=True,
        )

    def ping(self) -> bool:
        try:
            return bool(self._client.ping())
        except RedisError:
            return False

    def close(self) -> None:
        self._client.close()
