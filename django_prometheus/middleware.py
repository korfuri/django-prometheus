import django
from prometheus_client import Counter, Histogram

from django_prometheus.utils import Time, TimeSince, PowersOf

if django.VERSION >= (1, 10, 0):
    from django.utils.deprecation import MiddlewareMixin
else:
    MiddlewareMixin = object


ACCEPTABLE_HTTP_METHODS = (
    'connect',
    'delete',
    'get',
    'head',
    'options',
    'patch',
    'post',
    'put',
    'trace',
)


requests_total = Counter(
    'django_http_requests_before_middlewares_total',
    'Total count of requests before middlewares run.')
responses_total = Counter(
    'django_http_responses_before_middlewares_total',
    'Total count of responses before middlewares run.')
requests_latency_before = Histogram(
    'django_http_requests_latency_including_middlewares_seconds',
    ('Histogram of requests processing time (including middleware '
     'processing time).'))
requests_unknown_latency_before = Counter(
    'django_http_requests_unknown_latency_including_middlewares_total',
    ('Count of requests for which the latency was unknown (when computing '
     'django_http_requests_latency_including_middlewares_seconds).'))


class PrometheusBeforeMiddleware(MiddlewareMixin):

    """Monitoring middleware that should run before other middlewares."""
    def process_request(self, request):
        requests_total.inc()
        request.prometheus_before_middleware_event = Time()

    def process_response(self, request, response):
        responses_total.inc()
        if hasattr(request, 'prometheus_before_middleware_event'):
            requests_latency_before.observe(TimeSince(
                request.prometheus_before_middleware_event))
        else:
            requests_unknown_latency_before.inc()
        return response


requests_latency_by_view_method = Histogram(
    'django_http_requests_latency_seconds_by_view_method',
    'Histogram of request processing time labelled by view.',
    ['handler', 'method'])
requests_unknown_latency = Counter(
    'django_http_requests_unknown_latency_total',
    'Count of requests for which the latency was unknown.')
# Set in process_view
requests_body_bytes = Histogram(
    'django_http_requests_body_total_bytes',
    'Histogram of requests by body size.',
    buckets=PowersOf(2, 30))
# Set in process_template_response
http_template_responses = Counter(
    'django_http_template_responses',
    'Count of template responses.',
    ['template_name'],
)
# Set in process_response
http_responses = Counter(
    'django_http_responses',
    'Count of HTTP responses.',
    ['code', 'handler', 'method'],
)
responses_body_bytes = Histogram(
    'django_http_responses_body_total_bytes',
    'Histogram of responses by body size.',
    buckets=PowersOf(2, 30))
responses_streaming = Counter(
    'django_http_responses_streaming_total',
    'Count of streaming responses.')
# Set in process_exception
exceptions_by_view = Counter(
    'django_exceptions',
    'Count of exceptions.',
    ['handler', 'method'],
)


class PrometheusAfterMiddleware(MiddlewareMixin):

    """Monitoring middleware that should run after other middlewares."""

    def _method(self, request):
        method = request.method.lower()
        if method not in ACCEPTABLE_HTTP_METHODS:
            return 'invalid'
        return method

    def process_request(self, request):
        content_length = int(request.META.get('CONTENT_LENGTH') or 0)
        requests_body_bytes.observe(content_length)
        request.prometheus_after_middleware_event = Time()

    def _get_view_name(self, request):
        view_name = "<unnamed view>"
        if hasattr(request, 'resolver_match'):
            if request.resolver_match is not None:
                if request.resolver_match.view_name is not None:
                    view_name = request.resolver_match.view_name
        return view_name

    def process_template_response(self, request, response):
        if hasattr(response, 'template_name'):
            http_template_responses.labels(
                template_name=str(response.template_name),
            ).inc()
        return response

    def process_response(self, request, response):
        method = self._method(request)
        handler = self._get_view_name(request)
        http_responses.labels(
            code=str(response.status_code),
            handler=handler,
            method=method,
        ).inc()
        if hasattr(response, 'streaming') and response.streaming:
            responses_streaming.inc()
        if hasattr(response, 'content'):
            responses_body_bytes.observe(len(response.content))
        if hasattr(request, 'prometheus_after_middleware_event'):
            requests_latency_by_view_method.labels(
                handler=handler,
                method=method,
            ).observe(TimeSince(request.prometheus_after_middleware_event))
        else:
            requests_unknown_latency.inc()
        return response

    def process_exception(self, request, exception):
        handler = self._get_view_name(request)
        method = self._method(request)
        exceptions_by_view.labels(handler=handler, method=method).inc()
        return None
