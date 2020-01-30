from django.conf import settings


NAMESPACE = getattr(settings, 'PROMETHEUS_METRIC_NAMESPACE', '')
