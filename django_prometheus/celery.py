# encoding: utf-8

from __future__ import absolute_import, division, print_function

from celery.signals import after_task_publish
from prometheus_client import Counter

celery_queued_tasks = Counter(
    'celery_queued_tasks',
    'Tasks submitted to the Celery queue',
    ('exchange', 'routing_key', 'task'))


def after_task_publish_listener(body, exchange, routing_key, *args, **kwargs):
    celery_queued_tasks.labels(exchange, routing_key, body['task']).inc()


def register_metrics():
    after_task_publish.connect(after_task_publish_listener)
