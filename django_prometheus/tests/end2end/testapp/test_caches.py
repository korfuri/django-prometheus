from django.core.cache import caches
from django.test import TestCase
from redis import RedisError

from django_prometheus.testutils import assert_metric_equal, get_metric


class TestCachesMetrics(TestCase):
    """Test django_prometheus.caches metrics."""

    def test_counters(self):
        supported_caches = [
            "memcached.PyLibMCCache",
            "memcached.PyMemcacheCache",
            "filebased",
            "locmem",
            "redis",
        ]

        # Note: those tests require a memcached server running
        for supported_cache in supported_caches:
            tested_cache = caches[supported_cache]
            backend = supported_cache.split(".")[0]

            total_before = get_metric("django_cache_get_total", backend=backend) or 0
            hit_before = get_metric("django_cache_get_hits_total", backend=backend) or 0
            miss_before = get_metric("django_cache_get_misses_total", backend=backend) or 0

            tested_cache.set("foo1", "bar")
            tested_cache.get("foo1")
            tested_cache.get("foo1")
            tested_cache.get("foofoo")

            result = tested_cache.get("foofoo", default="default")

            assert result == "default"

            assert_metric_equal(total_before + 4, "django_cache_get_total", backend=backend)
            assert_metric_equal(hit_before + 2, "django_cache_get_hits_total", backend=backend)
            assert_metric_equal(
                miss_before + 2,
                "django_cache_get_misses_total",
                backend=backend,
            )

    def test_redis_cache_fail(self):
        # Note: test use fake service config (like if server was stopped)
        supported_cache = "redis"

        total_before = get_metric("django_cache_get_total", backend=supported_cache) or 0
        fail_before = get_metric("django_cache_get_fail_total", backend=supported_cache) or 0
        hit_before = get_metric("django_cache_get_hits_total", backend=supported_cache) or 0
        miss_before = get_metric("django_cache_get_misses_total", backend=supported_cache) or 0

        tested_cache = caches["stopped_redis_ignore_exception"]
        tested_cache.get("foo1")

        assert_metric_equal(hit_before, "django_cache_get_hits_total", backend=supported_cache)
        assert_metric_equal(miss_before, "django_cache_get_misses_total", backend=supported_cache)
        assert_metric_equal(total_before + 1, "django_cache_get_total", backend=supported_cache)
        assert_metric_equal(fail_before + 1, "django_cache_get_fail_total", backend=supported_cache)

        tested_cache = caches["stopped_redis"]
        with self.assertRaises(RedisError):
            tested_cache.get("foo1")

        assert_metric_equal(hit_before, "django_cache_get_hits_total", backend=supported_cache)
        assert_metric_equal(miss_before, "django_cache_get_misses_total", backend=supported_cache)
        assert_metric_equal(total_before + 2, "django_cache_get_total", backend=supported_cache)
        assert_metric_equal(fail_before + 2, "django_cache_get_fail_total", backend=supported_cache)

    def test_cache_version_support(self):
        supported_caches = [
            "memcached.PyLibMCCache",
            "memcached.PyMemcacheCache",
            "filebased",
            "locmem",
            "redis",
        ]

        # Note: those tests require a memcached server running
        for supported_cache in supported_caches:
            tested_cache = caches[supported_cache]

            tested_cache.set("foo1", "bar v.1", version=1)
            tested_cache.set("foo1", "bar v.2", version=2)

            assert "bar v.1" == tested_cache.get("foo1", version=1)
            assert "bar v.2" == tested_cache.get("foo1", version=2)
