from functools import lru_cache

from app.core.config import get_settings
from app.integrations.cache.base import CacheClient
from app.integrations.cache.redis_client import RedisCacheClient


@lru_cache
def get_cache_client() -> CacheClient:
    settings = get_settings()
    return RedisCacheClient(settings.redis_url)
