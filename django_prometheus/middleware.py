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


def addCounter(name, description, *args, **kwargs):
    return Counter(name, description, *args, **kwargs)


def addHistogram(name, description, *args, **kwargs):
    return Histogram(name, description, *args, **kwargs)


requests_total = addCounter(
    'django_http_requests_before_middlewares_total',
    'Total count of requests before middlewares run.')
responses_total = addCounter(
    'django_http_responses_before_middlewares_total',
    'Total count of responses before middlewares run.')
requests_latency = addHistogram(
    'django_http_requests_latency_including_middlewares_seconds',
    ('Histogram of requests processing time (including middleware '
     'processing time).'))


class PrometheusBeforeMiddleware(object):
    """Monitoring middleware that should run before other middlewares."""
    def process_request(self, request):
        requests_total.inc()
        request.prometheus_before_middleware_event = Time()

    def process_response(self, request, response):
        responses_total.inc()
        requests_latency.observe(TimeSince(
            request.prometheus_before_middleware_event))
        return response


requests_latency = addHistogram(
    'django_http_requests_latency_seconds',
    'Histogram of requests processing time.')
# Set in process_request
ajax_requests = addCounter(
    'django_http_ajax_requests_total',
    'Count of AJAX requests.')
requests_by_method = addCounter(
    'django_http_requests_total_by_method',
    'Count of requests by method.',
    ['method'])
requests_by_transport = addCounter(
    'django_http_requests_total_by_transport',
    'Count of requests by transport.',
    ['transport'])
# Set in process_view
requests_by_view = addCounter(
    'django_http_requests_total_by_view',
    'Count of requests by view.',
    ['view_name'])
requests_by_view_transport_method = addCounter(
    'django_http_requests_total_by_view_transport_method',
    'Count of requests by view, transport, method.',
    ['view', 'transport', 'method'])
requests_body_bytes = addHistogram(
    'django_http_requests_body_total_bytes',
    'Histogram of requests by body size.',
    buckets=PowersOf(2, 30))
# Set in process_template_response
responses_by_templatename = addCounter(
    'django_http_responses_total_by_templatename',
    'Count of responses by template name.',
    ['templatename'])
# Set in process_response
responses_by_status = addCounter(
    'django_http_responses_total_by_status',
    'Count of responses by status.',
    ['status'])
responses_body_bytes = addHistogram(
    'django_http_responses_body_total_bytes',
    'Histogram of responses by body size.',
    buckets=PowersOf(2, 30))
responses_by_charset = addCounter(
    'django_http_responses_total_by_charset',
    'Count of responses by charset. Django >=1.8 only.',
    ['charset'])
responses_streaming = addCounter(
    'django_http_responses_streaming_total',
    'Count of streaming responses.')
# Set in process_exception
exceptions_by_type = addCounter(
    'django_http_exceptions_total_by_type',
    'Count of exceptions by object type.',
    ['type'])
exceptions_by_view = addCounter(
    'django_http_exceptions_total_by_view',
    'Count of exceptions by view.',
    ['view_name'])


class PrometheusAfterMiddleware(object):
    """Monitoring middleware that should run after other middlewares."""
    def _transport(self, request):
        return 'https' if request.is_secure() else 'http'

    def _method(self, request):
        m = request.method
        if m not in ('GET', 'HEAD', 'POST', 'PUT', 'DELETE', 'TRACE',
                     'OPTIONS', 'CONNECT', 'PATCH'):
            return '<invalid method>'
        return m

    def process_request(self, request):
        transport = self._transport(request)
        method = self._method(request)
        requests_by_method.labels(method).inc()
        requests_by_transport.labels(transport).inc()
        if request.is_ajax():
            ajax_requests.inc()
        requests_body_bytes.observe(len(request.body))
        request.prometheus_after_middleware_event = Time()

    def process_view(self, request, view_func, *view_args, **view_kwargs):
        transport = self._transport(request)
        method = self._method(request)
        name = request.resolver_match.view_name or '<unnamed view>'
        requests_by_view.labels(name).inc()
        requests_by_view_transport_method.labels(
            name, transport, method).inc()

    def process_template_response(self, request, response):
        responses_by_templatename.labels(str(
            response.template_name)).inc()
        return response

    def process_response(self, request, response):
        responses_by_status.labels(str(response.status_code)).inc()
        if hasattr(response, 'charset'):
            responses_by_charset.labels(str(response.charset)).inc()
        if response.streaming:
            responses_streaming.inc()
        responses_body_bytes.observe(len(response.content))
        requests_latency.observe(TimeSince(
            request.prometheus_after_middleware_event))
        return response

    def process_exception(self, request, exception):
        name = request.resolver_match.view_name or '<unnamed view>'
        exceptions_by_type.labels(type(exception).__name__).inc()
        exceptions_by_view.labels(name).inc()
        requests_latency.observe(TimeSince(
            request.prometheus_after_middleware_event))


# The prometheus exporter is global, so we initialize it once in the
# global scope.
SetupPrometheusExports()
