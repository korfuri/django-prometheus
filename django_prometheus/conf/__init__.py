from django.conf import settings

NAMESPACE = ""

PROMETHEUS_LATENCY_BUCKETS = (
    0.01,
    0.025,
    0.05,
    0.075,
    0.1,
    0.25,
    0.5,
    0.75,
    1.0,
    2.5,
    5.0,
    7.5,
    10.0,
    25.0,
    50.0,
    75.0,
    float("inf"),
)

if settings.configured:
    NAMESPACE = getattr(settings, "PROMETHEUS_METRIC_NAMESPACE", NAMESPACE)
    PROMETHEUS_LATENCY_BUCKETS = getattr(settings, "PROMETHEUS_LATENCY_BUCKETS", PROMETHEUS_LATENCY_BUCKETS)
