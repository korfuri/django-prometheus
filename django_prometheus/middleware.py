from prometheus_client import Counter, Histogram, _INF
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


def PowersOf(logbase, count, lower=0):
    """Returns a list of count powers of logbase (from logbase**lower)."""
    return [logbase ** i for i in range(lower, count)] + [_INF]


class BasePrometheusMiddleware(object):
    """Common utilities for Prometheus middleware classes."""
    def addCounter(self, name, description, *args, **kwargs):
        return Counter(name, description, *args, **kwargs)

    def addHistogram(self, name, description, *args, **kwargs):
        return Histogram(name, description, *args, **kwargs)


class PrometheusBeforeMiddleware(BasePrometheusMiddleware):
    """Monitoring middleware that should run before other middlewares."""
    def __init__(self):
        self.requests_total = self.addCounter(
            'requests_total', 'Total count of requests')
        self.responses_total = self.addCounter(
            'responses_total', 'Total count of responses')
        SetupPrometheusExports()

    def process_request(self, request):
        self.requests_total.inc()

    def process_response(self, request, response):
        self.responses_total.inc()
        return response


class PrometheusAfterMiddleware(BasePrometheusMiddleware):
    """Monitoring middleware that should run after other middlewares."""
    def __init__(self):
        self.ajax_requests = self.addCounter(
            'ajax_requests',
            'Count of AJAX requests')
        self.requests_by_method = self.addCounter(
            'requests_by_method',
            'Count of requests by method',
            ['method'])
        self.requests_by_transport = self.addCounter(
            'requests_by_transport',
            'Count of requests by transport',
            ['transport'])
        self.requests_by_view = self.addCounter(
            'requests_by_view',
            'Count of requests by view',
            ['view_name'])
        self.requests_by_view_transport_method = self.addCounter(
            'requests_by_view_transport_method',
            'Count of requests by view, transport, method',
            ['view', 'transport', 'method'])
        self.requests_body_bytes = self.addHistogram(
            'requests_body_bytes',
            'Histogram of requests by body size',
            buckets=PowersOf(2, 30))
        self.responses_by_status = self.addCounter(
            'responses_by_status',
            'Count of responses by status',
            ['status'])
        self.responses_body_bytes = self.addHistogram(
            'responses_body_bytes',
            'Histogram of responses by body size',
            buckets=PowersOf(2, 30))

    def _transport(self, request):
        return 'https' if request.is_secure() else 'http'

    def process_request(self, request):
        transport = self._transport(request)
        self.requests_by_method.labels(request.method).inc()
        self.requests_by_transport.labels(transport).inc()
        if request.is_ajax():
            self.ajax_requests.inc()
        self.requests_body_bytes.observe(len(request.body))

    def process_view(self, request, view_func, *view_args, **view_kwargs):
        transport = self._transport(request)
        name = request.resolver_match.view_name or '<unnamed view>'
        self.requests_by_view.labels(name).inc()
        self.requests_by_view_transport_method.labels(
            name, transport, request.method).inc()

    def process_response(self, request, response):
        self.responses_by_status.labels(str(response.status_code)).inc()
        self.responses_body_bytes.observe(len(response.content))
        return response
