import logging
import os
import threading
import base64

import prometheus_client
from prometheus_client import multiprocess

from django.conf import settings
from django.http import HttpResponse

try:
    # Python 2
    from BaseHTTPServer import HTTPServer
except ImportError:
    # Python 3
    from http.server import HTTPServer


logger = logging.getLogger(__name__)


def SetupPrometheusEndpointOnPort(port, addr=""):
    """Exports Prometheus metrics on an HTTPServer running in its own thread.

    The server runs on the given port and is by default listenning on
    all interfaces. This HTTPServer is fully independent of Django and
    its stack. This offers the advantage that even if Django becomes
    unable to respond, the HTTPServer will continue to function and
    export metrics. However, this also means that the features
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
    assert os.environ.get("RUN_MAIN") != "true", (
        "The thread-based exporter can't be safely used when django's "
        "autoreloader is active. Use the URL exporter, or start django "
        "with --noreload. See documentation/exports.md."
    )
    prometheus_client.start_http_server(port, addr=addr)


class PrometheusEndpointServer(threading.Thread):
    """A thread class that holds an http and makes it serve_forever()."""

    def __init__(self, httpd, *args, **kwargs):
        self.httpd = httpd
        super().__init__(*args, **kwargs)

    def run(self):
        self.httpd.serve_forever()


def SetupPrometheusEndpointOnPortRange(port_range, addr=""):
    """Like SetupPrometheusEndpointOnPort, but tries several ports.

    This is useful when you're running Django as a WSGI application
    with multiple processes and you want Prometheus to discover all
    workers. Each worker will grab a port and you can use Prometheus
    to aggregate across workers.

    port_range may be any iterable object that contains a list of
    ports. Typically this would be a `range` of contiguous ports.

    As soon as one port is found that can serve, use this one and stop
    trying.

    Returns the port chosen (an `int`), or `None` if no port in the
    supplied range was available.

    The same caveats regarding autoreload apply. Do not use this when
    Django's autoreloader is active.
    """
    assert os.environ.get("RUN_MAIN") != "true", (
        "The thread-based exporter can't be safely used when django's "
        "autoreloader is active. Use the URL exporter, or start django "
        "with --noreload. See documentation/exports.md."
    )
    for port in port_range:
        try:
            httpd = HTTPServer((addr, port), prometheus_client.MetricsHandler)
        except OSError:
            # Python 2 raises socket.error, in Python 3 socket.error is an
            # alias for OSError
            continue  # Try next port
        thread = PrometheusEndpointServer(httpd)
        thread.daemon = True
        thread.start()
        logger.info("Exporting Prometheus /metrics/ on port %s" % port)
        return port  # Stop trying ports at this point
    logger.warning(
        "Cannot export Prometheus /metrics/ - " "no available ports in supplied range"
    )
    return None


def SetupPrometheusExportsFromConfig():
    """Exports metrics so Prometheus can collect them."""
    port = getattr(settings, "PROMETHEUS_METRICS_EXPORT_PORT", None)
    port_range = getattr(settings, "PROMETHEUS_METRICS_EXPORT_PORT_RANGE", None)
    addr = getattr(settings, "PROMETHEUS_METRICS_EXPORT_ADDRESS", "")
    if port_range:
        SetupPrometheusEndpointOnPortRange(port_range, addr)
    elif port:
        SetupPrometheusEndpointOnPort(port, addr)


def ExportToDjangoView(request):
    """Exports /metrics as a Django view.

    You can use django_prometheus.urls to map /metrics to this view.
    """
    if "prometheus_multiproc_dir" in os.environ:
        registry = prometheus_client.CollectorRegistry()
        multiprocess.MultiProcessCollector(registry)
    else:
        registry = prometheus_client.REGISTRY
    metrics_page = prometheus_client.generate_latest(registry)
    expected_username = getattr(settings, "DJANGO_PROMETHEUS_AUTHORIZATION_USERNAME", None)
    expected_password = getattr(settings, "DJANGO_PROMETHEUS_AUTHORIZATION_PASSWORD", None)
    if expected_password is not None and expected_username is not None:
        auth_header = request.META.get("HTTP_AUTHORIZATION", "")
        token_type, _, credentials = auth_header.partition(" ")
        if credentials == '':
            return HttpResponse("", status=400)

        received_auth_string = base64.b64decode(credentials).decode()
        if ':' not in received_auth_string:
            return HttpResponse("", status=400)

        received_username = received_auth_string.split(':')[0]
        received_password = received_auth_string.split(':')[1]

        valid_username = received_username == expected_username
        valid_password = received_password == expected_password

        if token_type != 'Basic' or not valid_username or not valid_password:
            return HttpResponse("", status=401)

    return HttpResponse(
        metrics_page, content_type=prometheus_client.CONTENT_TYPE_LATEST
    )
