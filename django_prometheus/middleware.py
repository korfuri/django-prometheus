from prometheus_client import Counter, Histogram
from django_prometheus.utils import Time, TimeSince, PowersOf
import django

if django.VERSION >= (1, 10, 0):
    from django.utils.deprecation import MiddlewareMixin
else:
    MiddlewareMixin = object

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
    ['view', 'method'])
requests_unknown_latency = Counter(
    'django_http_requests_unknown_latency_total',
    'Count of requests for which the latency was unknown.')
# Set in process_request
ajax_requests = Counter(
    'django_http_ajax_requests_total',
    'Count of AJAX requests.')
requests_by_method = Counter(
    'django_http_requests_total_by_method',
    'Count of requests by method.',
    ['method'])
requests_by_transport = Counter(
    'django_http_requests_total_by_transport',
    'Count of requests by transport.',
    ['transport'])
# Set in process_view
requests_by_view_transport_method = Counter(
    'django_http_requests_total_by_view_transport_method',
    'Count of requests by view, transport, method.',
    ['view', 'transport', 'method'])
requests_body_bytes = Histogram(
    'django_http_requests_body_total_bytes',
    'Histogram of requests by body size.',
    buckets=PowersOf(2, 30))
# Set in process_template_response
responses_by_templatename = Counter(
    'django_http_responses_total_by_templatename',
    'Count of responses by template name.',
    ['templatename'])
# Set in process_response
responses_by_status = Counter(
    'django_http_responses_total_by_status',
    'Count of responses by status.',
    ['status'])
responses_body_bytes = Histogram(
    'django_http_responses_body_total_bytes',
    'Histogram of responses by body size.',
    buckets=PowersOf(2, 30))
responses_by_charset = Counter(
    'django_http_responses_total_by_charset',
    'Count of responses by charset.',
    ['charset'])
responses_streaming = Counter(
    'django_http_responses_streaming_total',
    'Count of streaming responses.')
# Set in process_exception
exceptions_by_type = Counter(
    'django_http_exceptions_total_by_type',
    'Count of exceptions by object type.',
    ['type'])
exceptions_by_view = Counter(
    'django_http_exceptions_total_by_view',
    'Count of exceptions by view.',
    ['view_name'])


class PrometheusAfterMiddleware(MiddlewareMixin):

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

    def process_view(self, request, view_func, *view_args, **view_kwargs):
        transport = self._transport(request)
        method = self._method(request)
        if hasattr(request, 'resolver_match'):
            name = request.resolver_match.view_name or '<unnamed view>'
            requests_by_view_transport_method.labels(
                name, transport, method).inc()

    def process_template_response(self, request, response):
        if hasattr(response, 'template_name'):
            responses_by_templatename.labels(str(
                response.template_name)).inc()
        return response

    def process_response(self, request, response):
        responses_by_status.labels(str(response.status_code)).inc()
        if hasattr(response, 'charset'):
            responses_by_charset.labels(str(response.charset)).inc()
        if hasattr(response, 'streaming') and response.streaming:
            responses_streaming.inc()
        if hasattr(response, 'content'):
            responses_body_bytes.observe(len(response.content))
        if hasattr(request, 'prometheus_after_middleware_event'):
            requests_latency_by_view_method\
                .labels(
                    view=self._get_view_name(request),
                    method=request.method)\
                .observe(TimeSince(
                    request.prometheus_after_middleware_event
                ))
        else:
            requests_unknown_latency.inc()
        return response

    def process_exception(self, request, exception):
        exceptions_by_type.labels(type(exception).__name__).inc()
        if hasattr(request, 'resolver_match'):
            name = request.resolver_match.view_name or '<unnamed view>'
            exceptions_by_view.labels(name).inc()
        if hasattr(request, 'prometheus_after_middleware_event'):
            requests_latency_by_view_method\
                .labels(
                    view=self._get_view_name(request),
                    method=request.method)\
                .observe(TimeSince(
                    request.prometheus_after_middleware_event
                ))
        else:
            requests_unknown_latency.inc()
