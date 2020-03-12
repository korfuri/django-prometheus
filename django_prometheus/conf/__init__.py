import os

from django.conf import settings

NAMESPACE = ""

if settings.configured:
    try:
        NAMESPACE = settings.PROMETHEUS_METRIC_NAMESPACE
    except AttributeError:
        pass

NAMESPACE = os.getenv("PROMETHEUS_METRIC_NAMESPACE", NAMESPACE)
