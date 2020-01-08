import django
from prometheus_client import Counter, Histogram

from django_prometheus.utils import Time, TimeSince, PowersOf

if django.VERSION >= (1, 10, 0):
    from django.utils.deprecation import MiddlewareMixin
else:
    MiddlewareMixin = object

if django.VERSION < (1, 5, 0):
    from django.core.urlresolvers import resolve


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


http_request_duration = Histogram(
    'django_http_request_duration_seconds',
    ('Histogram of requests processing time (including middlewares).'),
    ['handler'],
    buckets=(
        .005, .01, .025, .05, .075, .1, .25, .5, .75, 1.0,
        2.5, 5.0, 7.5, 10.0, 15.0, 30.0, 60.0, 120.0, 300.0
    ),
)
http_request_size = Histogram(
    'django_http_request_size_bytes',
    'Histogram of requests by body size.',
    buckets=PowersOf(2, 30),
)
http_view_duration = Histogram(
    'django_view_duration_seconds',
    'Histogram of view processing duration.',
    ['handler'],
    buckets=(
        .005, .01, .025, .05, .075, .1, .25, .5, .75, 1.0,
        2.5, 5.0, 7.5, 10.0, 15.0, 30.0, 60.0, 120.0, 300.0
    ),
)
http_template_responses = Counter(
    'django_http_template_responses',
    'Count of template responses.',
    ['template_name'],
)
http_responses = Counter(
    'django_http_responses',
    'Count of HTTP responses.',
    ['code', 'handler', 'method'],
)
http_middleware_responses = Counter(
    'django_http_middleware_responses',
    'Count of HTTP responses originating from middlewares and not the view.',
    ['code', 'handler', 'method'],
)
http_response_size = Histogram(
    'django_http_response_size_bytes',
    'Histogram of responses by body size.',
    buckets=PowersOf(2, 30),
)
http_streaming_responses = Counter(
    'django_http_streaming_responses',
    'Count of streaming responses.',
)
exceptions_by_view = Counter(
    'django_exceptions',
    'Count of exceptions.',
    ['handler', 'method'],
)


def request_view_name(request):
    view_name = '<unnamed view>'
    if hasattr(request, 'resolver_match'):
        if request.resolver_match is not None:
            if request.resolver_match.view_name is not None:
                view_name = request.resolver_match.view_name
    elif django.VERSION < (1, 5, 0) and hasattr(request, 'path'):
        try:
            view_name = resolve(request.path).url_name
        except:  # No view match
            pass
    return view_name


def request_method(request):
    method = request.method.lower()
    if method not in ACCEPTABLE_HTTP_METHODS:
        return 'invalid'
    return method


class PrometheusBeforeMiddleware(MiddlewareMixin):

    """Monitoring middleware that should run before other middlewares."""
    def process_request(self, request):
        request.prometheus_before_middleware_event = Time()
        content_length = int(request.META.get('CONTENT_LENGTH') or 0)
        http_request_size.observe(content_length)

    def process_response(self, request, response):
        if hasattr(request, 'prometheus_before_middleware_event'):
            http_request_duration.labels(
                handler=request_view_name(request),
            ).observe(
                TimeSince(request.prometheus_before_middleware_event)
            )
        return response


class PrometheusAfterMiddleware(MiddlewareMixin):

    """Monitoring middleware that should run after other middlewares."""

    def process_request(self, request):
        request.prometheus_after_middleware_event = Time()

    def process_template_response(self, request, response):
        if hasattr(response, 'template_name'):
            http_template_responses.labels(
                template_name=str(response.template_name),
            ).inc()
        return response

    def process_response(self, request, response):
        code = str(response.status_code)
        handler = request_view_name(request)
        method = request_method(request)
        http_responses.labels(
            code=code,
            handler=handler,
            method=method,
        ).inc()
        if hasattr(response, 'streaming') and response.streaming:
            http_streaming_responses.inc()
        if hasattr(response, 'content'):
            http_response_size.observe(len(response.content))

        if hasattr(request, 'prometheus_after_middleware_event'):
            http_view_duration.labels(
                handler=handler,
            ).observe(TimeSince(request.prometheus_after_middleware_event))
        else:
            # In this case it means a middleware responded before the view
            http_middleware_responses.labels(
                code=code,
                handler=handler,
                method=method,
            ).inc()
        return response

    def process_exception(self, request, exception):
        handler = request_view_name(request)
        method = request_method(request)
        exceptions_by_view.labels(handler=handler, method=method).inc()
        return None
