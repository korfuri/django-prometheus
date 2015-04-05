from prometheus_client import MetricsHandler
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
    server_address = (addr, port)
    httpd = HTTPServer(server_address, MetricsHandler)
    thread.start_new_thread(httpd.serve_forever, ())


def SetupPrometheusExports():
    """Exports metrics so Prometheus can collect them."""
    # TODO(korfuri): add the option of exporting to Django. Use
    # django's settings to pick the export methods (possibly both at
    # the same time) and the port.
    SetupPrometheusEndpointOnPort(8001)


# The prometheus exporter is global, so we initialize it once in the
# global scope.
SetupPrometheusExports()
