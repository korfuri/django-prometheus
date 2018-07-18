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

            result = tested_cache.get('foofoo', default='default')

            assert result == 'default'

            self.assertMetricEquals(
                4, 'django_cache_get_total', backend=supported_cache)
            self.assertMetricEquals(
                2, 'django_cache_get_hits_total', backend=supported_cache)
            self.assertMetricEquals(
                2, 'django_cache_get_misses_total', backend=supported_cache)

    def test_cache_version_support(self):
        supported_caches = ['memcached', 'filebased', 'locmem']

        # Note: those tests require a memcached server running
        for supported_cache in supported_caches:
            tested_cache = caches[supported_cache]

            tested_cache.set('foo1', 'bar v.1', version=1)
            tested_cache.set('foo1', 'bar v.2', version=2)

            assert 'bar v.1' == tested_cache.get('foo1', version=1)
            assert 'bar v.2' == tested_cache.get('foo1', version=2)
