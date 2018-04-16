from unittest import skipUnless

from django_prometheus.testutils import PrometheusTestCaseMixin
from django.test import TestCase
from django.core.cache import caches


class TestCachesMetrics(PrometheusTestCaseMixin, TestCase):
    """Test django_prometheus.caches metrics."""

    def testCounters(self):
        cache_memcached = caches['memcached']
        cache_filebased = caches['filebased']

        cache_filebased.set('foo1', 'bar')
        cache_filebased.get('foo1')
        cache_filebased.get('foo1')
        cache_filebased.get('foofoo')

        self.assertMetricEquals(
            3, 'django_cache_get_total', backend='filebased')
        self.assertMetricEquals(
            2, 'django_cache_get_hits_total', backend='filebased')
        self.assertMetricEquals(
            1, 'django_cache_get_misses_total', backend='filebased')

        # Note: those tests require a memcached server running
        cache_memcached.set('foo2', 'bar')
        cache_memcached.get('foo2')
        cache_memcached.get('foofoo')
        cache_memcached.get('foofoo')

        self.assertMetricEquals(
            3, 'django_cache_get_total', backend='memcached')
        self.assertMetricEquals(
            1, 'django_cache_get_hits_total', backend='memcached')
        self.assertMetricEquals(
            2, 'django_cache_get_misses_total', backend='memcached')
