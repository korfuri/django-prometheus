from prometheus_client import Counter

from django_prometheus.conf import NAMESPACE

django_cache_get_total = Counter(
    "django_cache_get_total",
    "Total get requests on cache",
    ["backend"],
    namespace=NAMESPACE,
)
django_cache_hits_total = Counter(
    "django_cache_get_hits_total",
    "Total hits on cache",
    ["backend"],
    namespace=NAMESPACE,
)
django_cache_misses_total = Counter(
    "django_cache_get_misses_total",
    "Total misses on cache",
    ["backend"],
    namespace=NAMESPACE,
)
django_cache_get_fail_total = Counter(
    "django_cache_get_fail_total",
    "Total get request failures by cache",
    ["backend"],
    namespace=NAMESPACE,
)
