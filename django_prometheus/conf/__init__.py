from django.conf import settings

if not settings.configured:
    settings.configure()

NAMESPACE = getattr(settings, 'PROMETHEUS_METRIC_NAMESPACE', '')
