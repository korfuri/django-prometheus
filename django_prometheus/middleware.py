from prometheus_client import Counter, Histogram, _INF
from prometheus_client import MetricsHandler
from BaseHTTPServer import HTTPServer
import thread
from django_prometheus.utils import Time, TimeSince


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


def PowersOf(logbase, count, lower=0, include_zero=True):
    """Returns a list of count powers of logbase (from logbase**lower)."""
    if not include_zero:
        return [logbase ** i for i in range(lower, count)] + [_INF]
    else:
        return [0] + [logbase ** i for i in range(lower, count)] + [_INF]


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
            'django_http_requests_before_middlewares_total',
            'Total count of requests before middlewares run.')
        self.responses_total = self.addCounter(
            'django_http_responses_before_middlewares_total',
            'Total count of responses before middlewares run.')
        self.requests_latency = self.addHistogram(
            'django_http_requests_latency_including_middlewares_seconds',
            ('Histogram of requests processing time (including middleware '
             'processing time).'))
        SetupPrometheusExports()

    def process_request(self, request):
        self.requests_total.inc()
        request.prometheus_before_middleware_event = Time()

    def process_response(self, request, response):
        self.responses_total.inc()
        self.requests_latency.observe(TimeSince(
            request.prometheus_before_middleware_event))
        return response


class PrometheusAfterMiddleware(BasePrometheusMiddleware):
    """Monitoring middleware that should run after other middlewares."""
    def __init__(self):
        self.requests_latency = self.addHistogram(
            'django_http_requests_latency_seconds',
            'Histogram of requests processing time.')

        # Set in process_request
        self.ajax_requests = self.addCounter(
            'django_http_ajax_requests_total',
            'Count of AJAX requests.')
        self.requests_by_method = self.addCounter(
            'django_http_requests_total_by_method',
            'Count of requests by method.',
            ['method'])
        self.requests_by_transport = self.addCounter(
            'django_http_requests_total_by_transport',
            'Count of requests by transport.',
            ['transport'])

        # Set in process_view
        self.requests_by_view = self.addCounter(
            'django_http_requests_total_by_view',
            'Count of requests by view.',
            ['view_name'])
        self.requests_by_view_transport_method = self.addCounter(
            'django_http_requests_total_by_view_transport_method',
            'Count of requests by view, transport, method.',
            ['view', 'transport', 'method'])
        self.requests_body_bytes = self.addHistogram(
            'django_http_requests_body_total_bytes',
            'Histogram of requests by body size.',
            buckets=PowersOf(2, 30))

        # Set in process_template_response
        self.responses_by_templatename = self.addCounter(
            'django_http_responses_total_by_templatename',
            'Count of responses by template name.',
            ['templatename'])

        # Set in process_response
        self.responses_by_status = self.addCounter(
            'django_http_responses_total_by_status',
            'Count of responses by status.',
            ['status'])
        self.responses_body_bytes = self.addHistogram(
            'django_http_responses_body_total_bytes',
            'Histogram of responses by body size.',
            buckets=PowersOf(2, 30))
        self.responses_by_charset = self.addCounter(
            'django_http_responses_total_by_charset',
            'Count of responses by charset. Django >=1.8 only.',
            ['charset'])
        self.responses_streaming = self.addCounter(
            'django_http_responses_streaming_total',
            'Count of streaming responses.')

        # Set in process_exception
        self.exceptions_by_type = self.addCounter(
            'django_http_exceptions_total_by_type',
            'Count of exceptions by object type.',
            ['type'])
        self.exceptions_by_view = self.addCounter(
            'django_http_exceptions_total_by_view',
            'Count of exceptions by view.',
            ['view_name'])

    def _transport(self, request):
        return 'https' if request.is_secure() else 'http'

    def process_request(self, request):
        transport = self._transport(request)
        self.requests_by_method.labels(request.method).inc()
        self.requests_by_transport.labels(transport).inc()
        if request.is_ajax():
            self.ajax_requests.inc()
        self.requests_body_bytes.observe(len(request.body))
        request.prometheus_after_middleware_event = Time()

    def process_view(self, request, view_func, *view_args, **view_kwargs):
        transport = self._transport(request)
        name = request.resolver_match.view_name or '<unnamed view>'
        self.requests_by_view.labels(name).inc()
        self.requests_by_view_transport_method.labels(
            name, transport, request.method).inc()

    def process_template_response(self, request, response):
        self.responses_by_templatename.labels(response.template_name).inc()
        return response

    def process_response(self, request, response):
        self.responses_by_status.labels(str(response.status_code)).inc()
        self.responses_by_charset.labels(response.charset).inc()
        if response.streaming:
            self.responses_streaming.inc()
        self.responses_body_bytes.observe(len(response.content))
        self.requests_latency.observe(TimeSince(
            request.prometheus_after_middleware_event))
        return response

    def process_exception(self, request, exception):
        name = request.resolver_match.view_name or '<unnamed view>'
        self.exceptions_by_type.labels(type(exception).__name__).inc()
        self.exceptions_by_view.labels(name).inc()
        self.requests_latency.observe(TimeSince(
            request.prometheus_after_middleware_event))
