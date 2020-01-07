from datetime import datetime

from django.conf import settings
from django.core.management.base import BaseCommand

from prometheus_client import (
    CollectorRegistry,
    Counter,
    Gauge,
    push_to_gateway,
)
from prometheus_client.exposition import (
    default_handler,
    basic_auth_handler,
)


class PushgatewayCommand(BaseCommand):

    def __init__(self):
        assert self.job_name
        self.gateway_url = getattr(
            settings,
            'PUSHGATEWAY_URL',
            'http://localhost:9091',
        )
        self.gateway_user = getattr(settings, 'PUSHGATEWAY_USER', None)
        self.gateway_password = getattr(settings, 'PUSHGATEWAY_PASSWORD', None)
        if self.gateway_user and self.gateway_password:
            self.handler = self.auth_handler
        else:
            self.handler = default_handler
        self.registry = CollectorRegistry()
        self.duration = Gauge(
            'job_last_duration_seconds',
            'Last execution duration of a batch job',
            registry=self.registry,
        )
        self.start_datetime = datetime.now()
        super(PushgatewayCommand, self).__init__()

    def auth_handler(self, url, method, timeout, headers, data):
        return basic_auth_handler(
            url=url,
            method=method,
            timeout=timeout,
            headers=headers,
            data=data,
            username=self.gateway_user,
            password=self.gateway_password,
        )

    def gauge(self, name, description, labels=[]):
        return Gauge(name, description, labels, registry=self.registry)

    def counter(self, name, description, labels=[]):
        return Counter(name, description, labels, registry=self.registry)

    def push_metrics(self):
        self.duration.set(
            (datetime.now() - self.start_datetime).total_seconds()
        )
        push_to_gateway(
            self.gateway_url,
            job=self.job_name,
            registry=self.registry,
            handler=self.handler,
        )
