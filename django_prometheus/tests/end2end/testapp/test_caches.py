from django.core.cache import caches
from django.test import TestCase
from redis import RedisError

from django_prometheus.testutils import PrometheusTestCaseMixin


class TestCachesMetrics(PrometheusTestCaseMixin, TestCase):
    """Test django_prometheus.caches metrics."""

    def testCounters(self):
        supported_caches = ["memcached", "filebased", "locmem", "redis"]

        # Note: those tests require a memcached server running
        for supported_cache in supported_caches:
            tested_cache = caches[supported_cache]

            total_before = (
                self.getMetric("django_cache_get_total", backend=supported_cache) or 0
            )
            hit_before = (
                self.getMetric("django_cache_get_hits_total", backend=supported_cache)
                or 0
            )
            miss_before = (
                self.getMetric("django_cache_get_misses_total", backend=supported_cache)
                or 0
            )

            tested_cache.set("foo1", "bar")
            tested_cache.get("foo1")
            tested_cache.get("foo1")
            tested_cache.get("foofoo")

            result = tested_cache.get("foofoo", default="default")

            assert result == "default"

            self.assertMetricEquals(
                total_before + 4, "django_cache_get_total", backend=supported_cache
            )
            self.assertMetricEquals(
                hit_before + 2, "django_cache_get_hits_total", backend=supported_cache
            )
            self.assertMetricEquals(
                miss_before + 2,
                "django_cache_get_misses_total",
                backend=supported_cache,
            )

    def test_redis_cache_fail(self):

        # Note: test use fake service config (like if server was stopped)
        supported_cache = "redis"

        total_before = (
            self.getMetric("django_cache_get_total", backend=supported_cache) or 0
        )
        fail_before = (
            self.getMetric("django_cache_get_fail_total", backend=supported_cache) or 0
        )
        hit_before = (
            self.getMetric("django_cache_get_hits_total", backend=supported_cache) or 0
        )
        miss_before = (
            self.getMetric("django_cache_get_misses_total", backend=supported_cache)
            or 0
        )

        tested_cache = caches["stopped_redis_ignore_exception"]
        tested_cache.get("foo1")

        self.assertMetricEquals(
            hit_before, "django_cache_get_hits_total", backend=supported_cache
        )
        self.assertMetricEquals(
            miss_before, "django_cache_get_misses_total", backend=supported_cache
        )
        self.assertMetricEquals(
            total_before + 1, "django_cache_get_total", backend=supported_cache
        )
        self.assertMetricEquals(
            fail_before + 1, "django_cache_get_fail_total", backend=supported_cache
        )

        tested_cache = caches["stopped_redis"]
        with self.assertRaises(RedisError):
            tested_cache.get("foo1")

        self.assertMetricEquals(
            hit_before, "django_cache_get_hits_total", backend=supported_cache
        )
        self.assertMetricEquals(
            miss_before, "django_cache_get_misses_total", backend=supported_cache
        )
        self.assertMetricEquals(
            total_before + 2, "django_cache_get_total", backend=supported_cache
        )
        self.assertMetricEquals(
            fail_before + 2, "django_cache_get_fail_total", backend=supported_cache
        )

    def test_cache_version_support(self):
        supported_caches = ["memcached", "filebased", "locmem", "redis"]

        # Note: those tests require a memcached server running
        for supported_cache in supported_caches:
            tested_cache = caches[supported_cache]

            tested_cache.set("foo1", "bar v.1", version=1)
            tested_cache.set("foo1", "bar v.2", version=2)

            assert "bar v.1" == tested_cache.get("foo1", version=1)
            assert "bar v.2" == tested_cache.get("foo1", version=2)
