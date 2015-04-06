# django-prometheus
Export Django monitoring metrics for Prometheus.io

[![PyPI version](https://badge.fury.io/py/django-prometheus.svg)](http://badge.fury.io/py/django-prometheus)
[![Build Status](https://travis-ci.org/korfuri/django-prometheus.svg?branch=master)](https://travis-ci.org/korfuri/django-prometheus)

## Usage

### Requirements

* Django >= 1.8

### Installation

Install with:
```shell
pip install django-prometheus
```

Or, if you're using a development version cloned from this repository:
```shell
python path-to-where-you-cloned-django-prometheus/setup.py install
```

This will install [prometheus_client](https://github.com/prometheus/client_python) as a dependency.

### Configuration

In your settings.py:

```python
INSTALLED_APPS = (
   ...
   'django_prometheus',
   ...
)

MIDDLEWARE_CLASSES = (
    'django_prometheus.middleware.PrometheusBeforeMiddleware',
    # All your other middlewares go here, including the default
    # middlewares like SessionMiddleware, CommonMiddleware,
    # CsrfViewmiddleware, SecurityMiddleware, etc.
    'django_prometheus.middleware.PrometheusAfterMiddleware',
)
```

### Exporting metrics

Currently, the PrometheusBeforemiddleware will start an HTTP server in
a thread on port 8001 to export the metrics. This will become
configurable in the future.

#### Exporting metrics as a Django view

As an alternative, you can use
django_prometheus.exports.ExportToDjangoView to render `/metrics` as a
Django view. The easiest way to do so is to include
django_prometheus.urls in your root urlpatterns as such:

```python
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^monitoring/', include('django_prometheus.urls')),
    url(r'^admin/', include(admin.site.urls)),
    ...
]
```

This is not recommended if you can avoid it. The default method serves
`/metrics` in a dedicated thread with its own HTTP server, which
ensures that even if Django gets stuck, your monitoring will still
collect data. However, exporting as a Django view lets you use all the
features of Django, like IP restriction, authentication, logging, etc.

### Monitoring and aggregating the metrics

Prometheus is quite easy to set up. An example prometheus.conf to
scrape `127.0.0.1:8001` can be found in `examples/prometheus`.

Here's an example of a PromDash displaying some of the metrics
collected by django-prometheus:

![Example dashboard](https://raw.githubusercontent.com/korfuri/django-prometheus/master/examples/django-promdash.png)

## Adding your own metrics

You can add application-level metrics in your code by using
[prometheus_client](https://github.com/prometheus/client_python)
directly. The exporter is global and will pick up your metrics.

To add metrics to the Django internals, the easiest way is to extend
django-prometheus' classes. Please consider contributing your metrics,
pull requests are welcome. Make sure to read the Prometheus best
practices on
[instrumentation](http://prometheus.io/docs/practices/instrumentation/)
and [naming](http://prometheus.io/docs/practices/naming/).
