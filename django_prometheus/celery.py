from __future__ import absolute_import, unicode_literals
from datetime import datetime
import os

from billiard import current_process
from celery.signals import (
    after_task_publish,
    task_postrun,
    task_prerun,
    task_retry,
    worker_process_init,
    worker_process_shutdown,
    celeryd_init,
)
from prometheus_client import values, multiprocess, Counter, Histogram


WORKER_ID_OFFSET = 1001  # 1000 is Celery main process
task_start_time = None  # Used to measure task execution time

tasks_published = Counter(
    'celery_tasks_published',
    'Count of published tasks',
    ['task'],
)
tasks_retried = Counter(
    'celery_tasks_retried',
    'Count of retried tasks',
    ['task'],
)
tasks_executed = Counter(
    'celery_tasks_executed',
    'Count of executed (finished) tasks',
    ['task', 'state'],
)
task_duration = Histogram(
    'celery_task_duration_seconds',
    'Duration of task execution in seconds',
    ['task', 'state'],
)


@after_task_publish.connect
def on_after_task_publish(sender=None, headers=None, body=None, **kwargs):
    """Dispatched when a task has been sent to the broker.
    Note that this is executed in the process that sent the task.
    """
    try:
        task_name = headers['task']
    except:  # headers['task'] is not always available
        task_name = 'UNKNOWN'
    tasks_published.labels(task=task_name).inc()


@task_prerun.connect
def on_task_prerun(*args, **kwargs):
    """Dispatched before a task is executed."""
    global task_start_time
    task_start_time = datetime.now()


@task_postrun.connect
def on_task_postrun(task, state, **kwargs):
    """Dispatched after a task has been executed."""
    task_state = state.lower()
    task_execution_time = (datetime.now() - task_start_time).total_seconds()
    task_name = task.__module__ + "." + task.__name__

    task_duration.labels(
        task=task_name,
        state=task_state,
    ).observe(task_execution_time)
    tasks_executed.labels(task=task_name, state=task_state).inc()


@task_retry.connect
def on_task_retry(sender=None, **kwargs):
    """Dispatched when a task will be retried."""
    task_name = sender.__module__ + "." + sender.__name__  # sender is task
    tasks_retried.labels(task=task_name).inc()


@worker_process_init.connect
def on_worker_process_init(*args, **kwargs):
    """Make use of stable worker IDs to name the dbfiles."""
    values.ValueClass = values.MultiProcessValue(
        _pidFunc=lambda: current_process().index + WORKER_ID_OFFSET,
    )


@worker_process_shutdown.connect
def on_worker_process_shutdown(pid, exitcode, **kwargs):
    """Dispatched in all pool child processes just before they exit.
    We delete the dbfile at that time.
    """
    multiprocess.mark_process_dead(current_process().index + WORKER_ID_OFFSET)
