from django.core.cache.backends import memcached

from django_prometheus.cache.metrics import (
    django_cache_get_total,
    django_cache_hits_total,
    django_cache_misses_total,
)


class MemcachedCache(memcached.PyLibMCCache):
    """Inherit memcached to add metrics about hit/miss ratio"""

    def get(self, key, default=None, version=None):
        django_cache_get_total.labels(backend="memcached").inc()
        cached = super().get(key, default=None, version=version)
        if cached is not None:
            django_cache_hits_total.labels(backend="memcached").inc()
        else:
            django_cache_misses_total.labels(backend="memcached").inc()
        return cached or default
