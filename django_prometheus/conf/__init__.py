from django.conf import settings

NAMESPACE = ""

if settings.configured:
    NAMESPACE = getattr(settings, "PROMETHEUS_METRIC_NAMESPACE", NAMESPACE)
