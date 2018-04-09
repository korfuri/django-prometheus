from django.core.cache.backends import filebased
from prometheus_client import Counter

django_cache_get_total = Counter('django_cache_get_total', 'Total get requests on cache')
django_cache_hits_total = Counter('django_cache_get_hits_total', 'Total hits on cache')
django_cache_misses_total = Counter('django_cache_get_misses_total', 'Total misses on cache')

class FileBasedCache(filebased.FileBasedCache):
    def get(self, key, default=None, version=None):
        django_cache_get_total.inc()
        cached = super().get(key, default=None, version=None)
        if cached:
            django_cache_hits_total.inc()
        else:
            django_cache_misses_total.inc()
        return cached
