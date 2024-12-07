from warnings import deprecated
from django.core.cache.backends.redis import RedisCache

from django_prometheus.cache.metrics import (
    django_cache_get_fail_total,
    django_cache_get_total,
    django_cache_hits_total,
    django_cache_misses_total,
)


class NativeRedisCache(RedisCache):
    def get(self, key, default=None, version=None):
        django_cache_get_total.labels(backend="native_redis").inc()
        try:
            result = super().get(key, default=None, version=version)
        except Exception:
            django_cache_get_fail_total.labels(backend="native_redis").inc()
            raise
        if result is not None:
            django_cache_hits_total.labels(backend="native_redis").inc()
            return result
        else:
            django_cache_misses_total.labels(backend="native_redis").inc()
            return default

RedisCache = deprecated("RedisCache is deprecated, use NativeRedisCache instead")(NativeRedisCache)
