from django.http import HttpResponse
import prometheus_client
from BaseHTTPServer import HTTPServer
import thread


def SetupPrometheusEndpointOnPort(port, addr=''):
    """Exports Prometheus metrics on an HTTPServer running in its own thread.

    The server runs on the given port and is by default listenning on
    all interfaces. This HTTPServer is fully independent of Django and
    its stack. This offers the advantage that even if Django becomes
    unable to respond, the HTTPServer will continue to function and
    export metrics. However, this also means that none of the features
    offered by Django (like middlewares or WSGI) can't be used.
    """
    prometheus_client.start_http_server(port, addr=addr)


def SetupPrometheusExports():
    """Exports metrics so Prometheus can collect them."""
    SetupPrometheusEndpointOnPort(8001)


def ExportToDjangoView(request):
    """Exports /metrics as a Django view.

    You can use django_prometheus.urls to map /metrics to this view.
    """
    metrics_page = generate_latest()
    return HttpResponse(
        metrics_page,
        content_type=prometheus_client.CONTENT_TYPE_LATEST)


# The prometheus exporter is global, so we initialize it once in the
# global scope.
SetupPrometheusExports()
