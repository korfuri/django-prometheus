# Exports

## Default: exporting /metrics as a Django view

/metrics can be exported as a Django view very easily. Simply
include('django_prometheus.urls') with no prefix like so:

```python
urlpatterns = [
    ...
    url('', include('django_prometheus.urls')),
]
```

This will reserve the /metrics path on your server. This may be a
problem for you, so you can use a prefix. For instance, the following
will export the metrics at `/monitoring/metrics` instead. You will
need to configure Prometheus to use that path instead of the default.

```python
urlpatterns = [
    ...
    url('^monitoring/', include('django_prometheus.urls')),
]
```

## Exporting /metrics in a dedicated thread

To ensure that issues in your Django app do not affect the monitoring,
it is recommended to export /metrics in an HTTPServer running in a
daemon thread. This will prevent that problems such as thread
starvation or low-level bugs in Django do not affect the export of
your metrics, which may be more needed than ever if these problems
occur.

It can be enabled by adding the following line in your `settings.py`:

```python
PROMETHEUS_METRICS_EXPORT_PORT = 8001
PROMETHEUS_METRICS_EXPORT_ADDRESS = ''  # all addresses
```

However, by default this mechanism is disabled, because it is not
compatible with Django's autoreloader. The autoreloader is the feature
that allows you to edit your code and see the changes
immediately. This works by forking multiple processes of Django, which
would compete for the port. As such, this code will assert-fail if the
autoreloader is active.

You can run Django without the autoreloader by passing `-noreload` to
`manage.py`. If you decide to enable the thread-based exporter in
production, you may wish to modify your manage.py to ensure that this
option is always active:

```python
    execute_from_command_line(sys.argv + ['--noreload'])
```

## Exporting /metrics in a WSGI application with multiple processes per process

If you're using WSGI (e.g. with uwsgi or with gunicorn) and multiple
Django processes, using either option above won't work, as requests
using the Django view would just go to an inconsistent backend each
time, and exporting on a single port doesn't work.

The following settings can be used instead:

```python
PROMETHEUS_METRICS_EXPORT_PORT_RANGE = xrange(8001, 8050)
```

This will make Django-Prometheus try to export /metrics on port
8001. If this fails (i.e. the port is in use), it will try 8002, then
8003, etc.

You can then configure Prometheus to collect metrics on as many
targets as you have workers, using each port separately.

## Exporting /metrics in a WSGI application with multiple processes globally

In some WSGI application, worker are short lived (less than a minute) so some
are never scrapped by prometheus by default. Prometheus client already provide
a nice system to aggregate them using the env variable: ```prometheus_multiproc_dir```
that will contain the directory where metrics will be stored.

Configuration in uwsgi will look like:

```
env = prometheus_multiproc_dir=/path/to/django_metrics
```

By default this will create four files (one for counters, one for summaries, ...etc)
for each pid used. In uwsgi, the number of different pids used can be quite large
(the pid change every time a worker respawn). To prevent having thousand of files
created, it's possible to create file using worker ids rather than pids.

It should be in settings, before any metric are created:

```python
from prometheus_client import core
import uwsgi
# Use uwsgi's worker_id rather than system pids
core._ValueClass = core._MultiProcessValue(_pidFunc=uwsgi.worker_id)
```

The number of resulting files will be:
number of processes * 4 (counter, histogram, gauge, summary)

Be aware that by default this will generate a large amount of file descriptors:
Each worker will keep 3 file descriptors for each files it created.

If uwsgi is not using lazy-apps (lazy-apps = true), there will be a
file descriptors leak (tens to hundreds of fds on a single file) due
to the way uwsgi forks processes to create workers.
