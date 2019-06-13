"""Django-Prometheus

https://github.com/korfuri/django-prometheus
"""
# Import all files that define metrics. This has the effect that
# `import django_prometheus` will always instanciate all metric
# objects right away.
from django_prometheus import middleware
from django_prometheus import models

__all__ = ['middleware', 'models', 'pip_prometheus']

# Import pip_prometheus to export the pip metrics automatically.
try:
    import pip_prometheus
except ImportError:
    # If people don't have pip, don't export anything.
    pass

default_app_config = 'django_prometheus.apps.DjangoPrometheusConfig'
