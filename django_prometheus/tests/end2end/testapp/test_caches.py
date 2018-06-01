from unittest import skipUnless

from django_prometheus.testutils import PrometheusTestCaseMixin
from django.test import TestCase
from django.core.cache import caches


class TestCachesMetrics(PrometheusTestCaseMixin, TestCase):
    """Test django_prometheus.caches metrics."""

    def testCounters(self):
        supported_caches = ['memcached', 'filebased', 'locmem']

        # Note: those tests require a memcached server running
        for supported_cache in supported_caches:
            tested_cache = caches[supported_cache]

            tested_cache.set('foo1', 'bar')
            tested_cache.get('foo1')
            tested_cache.get('foo1')
            tested_cache.get('foofoo')

            self.assertMetricEquals(
                3, 'django_cache_get_total', backend=supported_cache)
            self.assertMetricEquals(
                2, 'django_cache_get_hits_total', backend=supported_cache)
            self.assertMetricEquals(
                1, 'django_cache_get_misses_total', backend=supported_cache)
