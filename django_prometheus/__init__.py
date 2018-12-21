import os
from prometheus_client import values


# Override pid function if we have a reusable gunicorn worker ID
if os.environ.get('prometheus_multiproc_dir', None):  # noqa
    values.ValueClass = values.MultiProcessValue(
        _pidFunc=lambda: os.environ.get('APP_WORKER_ID', 1000),
    )

# Import all files that define metrics. This has the effect that
# `import django_prometheus` will always instanciate all metric
# objects right away.
import django_prometheus.middleware
import django_prometheus.models

# Import pip_prometheus to export the pip metrics automatically.
try:
    import pip_prometheus
except ImportError:
    # If people don't have pip, don't export anything.
    pass

try:  # Load celery exporter if possible
    import django_prometheus.celery
except ImportError:
    pass

default_app_config = 'django_prometheus.apps.DjangoPrometheusConfig'
