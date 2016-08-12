# encoding: utf-8
"""Celery metrics for Prometheus

There are two levels of monitoring available:

1. The `celery_queued_tasks` counter which is incremented each time a task is queued
   and is exposed along with all of the other metrics collected by django-prometheus
2. Since Celery tasks execute in a separate process, collecting their metrics requires
   use of the Prometheus push-gateway to aggregate the metrics sent from the transient
   worker processes.

   Set the ``PROMETHEUS_PUSH_GATEWAY`` setting to the hostname and port which
   your pushgateway server is running on::

    PROMETHEUS_PUSH_GATEWAY = 'localhost:9091'

   The job ID can be customized by setting `PROMETHEUS_PUSH_GATEWAY_JOB_ID`

   See https://prometheus.io/docs/instrumenting/pushing/ for more information about
   the push-gateway.
"""

from __future__ import absolute_import, division, print_function

from functools import partial
from timeit import default_timer

from celery.signals import after_task_publish, task_postrun, task_prerun
from celery.utils.log import get_task_logger
from prometheus_client import CollectorRegistry, Counter, Summary, pushadd_to_gateway

celery_queued_tasks = Counter(
    'celery_queued_tasks',
    'Tasks submitted to the Celery queue',
    ('exchange', 'routing_key', 'task'))

# We'll use this for every metric which is going to be pushed rather than scraped:
push_registry = CollectorRegistry()

celery_tasks_started = Counter(
    'celery_tasks_started',
    'Tasks started by a Celery worker',
    ('task', ),
    registry=push_registry
)

celery_tasks_completed = Counter(
    'celery_tasks_completed',
    'Celery tasks which completed',
    ('task', 'state'),
    registry=push_registry
)

celery_tasks_revoked = Counter(
    'celery_tasks_revoked',
    'Celery tasks which were revoked or terminated',
    ('task', 'terminated', 'expired', 'signal'),
    registry=push_registry
)

celery_tasks_elapsed_time = Summary(
    'celery_tasks_elapsed_time',
    'Celery tasks cumulative elapsed time',
    ('task', 'state'),
    registry=push_registry
)

# We need to record when a task started so we can record the elapsed time
# when it completes:
TASK_START_TIMES = {}


def after_task_publish_listener(body, exchange, routing_key, *args, **kwargs):
    celery_queued_tasks.labels(exchange, routing_key, body['task']).inc()


def task_prerun_listener(task_id=None, task=None, push_gateway=None, job_id=None, **kwargs):
    TASK_START_TIMES[task_id] = default_timer()
    celery_tasks_started.labels(task.name).inc()

    pushadd_to_gateway(push_gateway, job=job_id, registry=push_registry)


def task_postrun_listener(task_id=None, task=None, state=None, push_gateway=None, job_id=None, **kwargs):
    if task_id not in TASK_START_TIMES:
        get_task_logger().error('task_postrun called for unregistered task ID: %s', task_id)
        return

    elapsed_time = default_timer() - TASK_START_TIMES.pop(task_id)

    celery_tasks_completed.labels(task.name, state).inc()
    celery_tasks_elapsed_time.labels(task.name, state).observe(elapsed_time)

    pushadd_to_gateway(push_gateway, job=job_id, registry=push_registry)


def register_metrics():
    after_task_publish.connect(after_task_publish_listener)


def enable_push_gateway(push_gateway, job_id):
    # We'll use `partial` to bind the passed `push_gateway` and `job_id` values in the listeners
    # so we don't need to stash them in a global variable. Note the necessity to use weak=False to avoid our
    # partial functions being garbage-collected after this function returns:
    task_prerun.connect(partial(task_prerun_listener, push_gateway=push_gateway, job_id=job_id),
                        weak=False)
    task_postrun.connect(partial(task_postrun_listener, push_gateway=push_gateway, job_id=job_id),
                         weak=False)
