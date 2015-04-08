from django.http import HttpResponse
from django.conf import settings
import os
import prometheus_client


def SetupPrometheusEndpointOnPort(port, addr=''):
    """Exports Prometheus metrics on an HTTPServer running in its own thread.

    The server runs on the given port and is by default listenning on
    all interfaces. This HTTPServer is fully independent of Django and
    its stack. This offers the advantage that even if Django becomes
    unable to respond, the HTTPServer will continue to function and
    export metrics. However, this also means that none of the features
    offered by Django (like middlewares or WSGI) can't be used.

    Now here's the really weird part. When Django runs with the
    auto-reloader enabled (which is the default, you can disable it
    with `manage.py runserver --noreload`), it forks and executes
    manage.py twice. That's wasteful but usually OK. It starts being a
    problem when you try to open a port, like we do. We can detect
    that we're running under an autoreloader through the presence of
    the RUN_MAIN environment variable, so we abort if we're trying to
    export under an autoreloader and trying to open a port.
    """
    assert os.environ.get('RUN_MAIN') != 'true', (
        'The thread-based exporter can\'t be safely used when django\'s '
        'autoreloader is active. Use the URL exporter, or start django '
        'with --noreload. See documentation/exports.md.')
    prometheus_client.start_http_server(port, addr=addr)


def SetupPrometheusExportsFromConfig():
    """Exports metrics so Prometheus can collect them."""
    port = getattr(settings, 'PROMETHEUS_METRICS_EXPORT_PORT', None)
    addr = getattr(settings, 'PROMETHEUS_METRICS_EXPORT_ADDRESS', None)
    if port:
        SetupPrometheusEndpointOnPort(port, addr)


def ExportToDjangoView(request):
    """Exports /metrics as a Django view.

    You can use django_prometheus.urls to map /metrics to this view.
    """
    metrics_page = prometheus_client.generate_latest()
    return HttpResponse(
        metrics_page,
        content_type=prometheus_client.CONTENT_TYPE_LATEST)
