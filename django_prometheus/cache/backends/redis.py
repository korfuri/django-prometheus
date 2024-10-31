from django import VERSION as DJANGO_VERSION

from django_prometheus.cache.metrics import (
    django_cache_get_fail_total,
    django_cache_get_total,
    django_cache_hits_total,
    django_cache_misses_total,
)

try:
    from django_redis import cache, exceptions

    class RedisCache(cache.RedisCache):
        """Inherit redis to add metrics about hit/miss/interruption ratio"""

        @cache.omit_exception
        def get(self, key, default=None, version=None, client=None):
            try:
                django_cache_get_total.labels(backend="redis").inc()
                cached = self.client.get(key, default=None, version=version, client=client)
            except exceptions.ConnectionInterrupted as e:
                django_cache_get_fail_total.labels(backend="redis").inc()
                if self._ignore_exceptions:
                    if self._log_ignored_exceptions:
                        cache.logger.error(str(e))
                    return default
                raise
            else:
                if cached is not None:
                    django_cache_hits_total.labels(backend="redis").inc()
                    return cached
                else:
                    django_cache_misses_total.labels(backend="redis").inc()
                    return default
except ImportError:
    pass


if DJANGO_VERSION >= (4, 0):
    from django.core.cache.backends.redis import RedisCache as DjangoRedisCache

    class NativeRedisCache(DjangoRedisCache):
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
