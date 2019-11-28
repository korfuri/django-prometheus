from django.core.cache import caches
from django.test import TestCase
from django_prometheus.testutils import PrometheusTestCaseMixin
from redis import RedisError

_TOTAL = "django_cache_get_total"
_HIT = "django_cache_get_hits_total"
_MISS = "django_cache_get_misses_total"
_FAIL = "django_cache_get_fail_total"

_REDIS = "redis"
_REDIS2 = "redis_2"

_ALL_CACHES = ["memcached", "filebased", "locmem", _REDIS, _REDIS2]
_VERSIONED_CACHES = ["memcached", "filebased", "locmem", _REDIS]


class TestCachesMetrics(PrometheusTestCaseMixin, TestCase):
    """Test django_prometheus.caches metrics."""

    def testCounters(self):

        # Note: those tests require a memcached server running
        for supported_cache in _ALL_CACHES:
            tested_cache = caches[supported_cache]
            tested_cache.set("foo1", "bar")

            # initial counters
            total_before = self.getMetric(_TOTAL, backend=supported_cache)
            hit_before = self.getMetric(_HIT, backend=supported_cache)
            miss_before = self.getMetric(_MISS, backend=supported_cache)

            self.assertEqual(tested_cache.get("foo1"), "bar")
            self.assertEqual(tested_cache.get("foo1"), "bar")
            self.assertIsNone(tested_cache.get("foo2"))
            self.assertEqual(tested_cache.get("foo2", default="default"), "default")

            self.assertMetricEquals(
                (total_before or 0) + 4, _TOTAL, backend=supported_cache
            )
            self.assertMetricEquals(
                (hit_before or 0) + 2, _HIT, backend=supported_cache
            )
            self.assertMetricEquals(
                (miss_before or 0) + 2, _MISS, backend=supported_cache
            )

    def test_cache_version_support(self):
        supported_caches = _VERSIONED_CACHES

        # Note: those tests require a memcached server running
        for supported_cache in supported_caches:
            tested_cache = caches[supported_cache]

            tested_cache.set("foo1", "bar v.1", version=1)
            tested_cache.set("foo1", "bar v.2", version=2)

            self.assertEqual(tested_cache.get("foo1", version=1), "bar v.1")
            self.assertEqual(tested_cache.get("foo1", version=2), "bar v.2")

    def test_redis_cache_fail(self):

        # Note: test use fake service config (like if server was stopped)
        supported_cache = _REDIS

        total_before = self.getMetric(_TOTAL, backend=supported_cache)
        fail_before = self.getMetric(_FAIL, backend=supported_cache)
        hit_before = self.getMetric(_HIT, backend=supported_cache)
        miss_before = self.getMetric(_MISS, backend=supported_cache)

        tested_cache = caches["stopped_redis_ignore_exception"]
        tested_cache.get("foo1")

        self.assertMetricEquals(
            (total_before or 0) + 1, _TOTAL, backend=supported_cache
        )
        self.assertMetricEquals((fail_before or 0) + 1, _FAIL, backend=supported_cache)
        self.assertMetricEquals(hit_before, _HIT, backend=supported_cache)
        self.assertMetricEquals(miss_before, _MISS, backend=supported_cache)

        tested_cache = caches["stopped_redis"]
        with self.assertRaises(RedisError):
            tested_cache.get("foo1")

        self.assertMetricEquals(
            (total_before or 0) + 2, _TOTAL, backend=supported_cache
        )
        self.assertMetricEquals((fail_before or 0) + 2, _FAIL, backend=supported_cache)
        self.assertMetricEquals(hit_before, _HIT, backend=supported_cache)
        self.assertMetricEquals(miss_before, _MISS, backend=supported_cache)

    def test_redis2_cache_fail(self):

        # Note: test use fake service config (like if server was stopped)
        supported_cache = _REDIS2
        tested_cache = caches["stopped_redis_2"]

        total_before = self.getMetric(_TOTAL, backend=supported_cache)
        fail_before = self.getMetric(_FAIL, backend=supported_cache)
        hit_before = self.getMetric(_HIT, backend=supported_cache)
        miss_before = self.getMetric(_MISS, backend=supported_cache)

        with self.assertRaises(RedisError):
            tested_cache.get("foo1")

        self.assertMetricEquals(
            (total_before or 0) + 1, _TOTAL, backend=supported_cache
        )
        self.assertMetricEquals((fail_before or 0) + 1, _FAIL, backend=supported_cache)
        self.assertMetricEquals(hit_before, _HIT, backend=supported_cache)
        self.assertMetricEquals(miss_before, _MISS, backend=supported_cache)
