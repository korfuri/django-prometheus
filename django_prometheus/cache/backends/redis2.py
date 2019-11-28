from django_prometheus.cache.metrics import (
    django_cache_get_fail_total,
    django_cache_get_total,
    django_cache_hits_total,
    django_cache_misses_total,
)
from redis_cache.backends.single import RedisCache as SingleRedisCache

_REDIS2_BACKEND = "redis_2"


class RedisCache(SingleRedisCache):
    """Inherit redis to add metrics about hit/miss/interruption ratio."""

    def get(self, key, default=None):
        django_cache_get_total.labels(backend=_REDIS2_BACKEND).inc()

        try:
            cached = super(RedisCache, self).get(key, default=None)
            if cached is not None:
                django_cache_hits_total.labels(backend=_REDIS2_BACKEND).inc()
                return cached

            django_cache_misses_total.labels(backend=_REDIS2_BACKEND).inc()
            return default
        except Exception:
            django_cache_get_fail_total.labels(backend=_REDIS2_BACKEND).inc()
            raise
