from django.apps import AppConfig
from django.conf import settings

from django_prometheus.exports import SetupPrometheusExportsFromConfig
from django_prometheus.migrations import ExportMigrations

# unused import to force instantiating the metric objects at startup.
import django_prometheus


class DjangoPrometheusConfig(AppConfig):
    name = 'django_prometheus'
    verbose_name = 'Django-Prometheus'

    def ready(self):
        """Initializes the Prometheus exports if they are enabled in the config.

        Note that this is called even for other management commands
        than `runserver`. As such, it is possible to scrape the
        metrics of a running `manage.py test` or of another command,
        which shouldn't be done for real monitoring (since these jobs
        are usually short-lived), but can be useful for debugging.
        """
        SetupPrometheusExportsFromConfig()
        ExportMigrations()

        # Celery not longer reliably has something like `djcelery` in INSTALLED_APPS
        # so we'll use a setting to trigger generic registry. This also allows users
        # register the task listener only for specific senders.
        if getattr(settings, 'PROMETHEUS_MONITOR_CELERY', False):
            from . import celery
            celery.register_metrics()

            push_gateway = getattr(settings, 'PROMETHEUS_PUSH_GATEWAY', None)
            if push_gateway:
                job_id = getattr(settings, 'PROMETHEUS_PUSH_GATEWAY_JOB_ID', 'celery')
                celery.enable_push_gateway(push_gateway, job_id)
