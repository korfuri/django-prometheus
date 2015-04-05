# django-prometheus
Export Django monitoring metrics for Prometheus.io

## Usage

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

### Exported metrics

Currently, the PrometheusBeforemiddleware will start an HTTP server in
a thread on port 8001 to export the metrics. This will become
configurable in the future.
