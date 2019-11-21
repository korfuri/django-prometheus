from prometheus_client import Counter, Histogram

from django.conf import settings
from django.utils.deprecation import MiddlewareMixin
from django_prometheus.utils import PowersOf, Time, TimeSince

DEFAULT_LATENCY_BUCKETS = (
    0.01,
    0.025,
    0.05,
    0.075,
    0.1,
    0.25,
    0.5,
    0.75,
    1.0,
    2.5,
    5.0,
    7.5,
    10.0,
    25.0,
    50.0,
    75.0,
    float("inf"),
)


class Metrics:
    _instance = None

    @classmethod
    def get_instance(cls):
        if not cls._instance:
            cls._instance = cls()
        return cls._instance

    def register_metric(
        self, metric_cls, name, documentation, labelnames=tuple(), **kwargs
    ):
        return metric_cls(name, documentation, labelnames=labelnames, **kwargs)

    def __init__(self, *args, **kwargs):
        self.register()

    def register(self):
        self.requests_total = self.register_metric(
            Counter,
            "django_http_requests_before_middlewares_total",
            "Total count of requests before middlewares run.",
        )
        self.responses_total = self.register_metric(
            Counter,
            "django_http_responses_before_middlewares_total",
            "Total count of responses before middlewares run.",
        )
        self.requests_latency_before = self.register_metric(
            Histogram,
            "django_http_requests_latency_including_middlewares_seconds",
            (
                "Histogram of requests processing time (including middleware "
                "processing time)."
            ),
        )
        self.requests_unknown_latency_before = self.register_metric(
            Counter,
            "django_http_requests_unknown_latency_including_middlewares_total",
            (
                "Count of requests for which the latency was unknown (when computing "
                "django_http_requests_latency_including_middlewares_seconds)."
            ),
        )
        self.requests_latency_by_view_method = self.register_metric(
            Histogram,
            "django_http_requests_latency_seconds_by_view_method",
            "Histogram of request processing time labelled by view.",
            ["view", "method"],
            buckets=getattr(
                settings, "PROMETHEUS_LATENCY_BUCKETS", DEFAULT_LATENCY_BUCKETS
            ),
        )
        self.requests_unknown_latency = self.register_metric(
            Counter,
            "django_http_requests_unknown_latency_total",
            "Count of requests for which the latency was unknown.",
        )
        # Set in process_request
        self.requests_ajax = self.register_metric(
            Counter, "django_http_ajax_requests_total", "Count of AJAX requests."
        )
        self.requests_by_method = self.register_metric(
            Counter,
            "django_http_requests_total_by_method",
            "Count of requests by method.",
            ["method"],
        )
        self.requests_by_transport = self.register_metric(
            Counter,
            "django_http_requests_total_by_transport",
            "Count of requests by transport.",
            ["transport"],
        )
        # Set in process_view
        self.requests_by_view_transport_method = self.register_metric(
            Counter,
            "django_http_requests_total_by_view_transport_method",
            "Count of requests by view, transport, method.",
            ["view", "transport", "method"],
        )
        self.requests_body_bytes = self.register_metric(
            Histogram,
            "django_http_requests_body_total_bytes",
            "Histogram of requests by body size.",
            buckets=PowersOf(2, 30),
        )
        # Set in process_template_response
        self.responses_by_templatename = self.register_metric(
            Counter,
            "django_http_responses_total_by_templatename",
            "Count of responses by template name.",
            ["templatename"],
        )
        # Set in process_response
        self.responses_by_status = self.register_metric(
            Counter,
            "django_http_responses_total_by_status",
            "Count of responses by status.",
            ["status"],
        )
        self.responses_by_status_view_method = self.register_metric(
            Counter,
            "django_http_responses_total_by_status_view_method",
            "Count of responses by status, view, method.",
            ["status", "view", "method"],
        )
        self.responses_body_bytes = self.register_metric(
            Histogram,
            "django_http_responses_body_total_bytes",
            "Histogram of responses by body size.",
            buckets=PowersOf(2, 30),
        )
        self.responses_by_charset = self.register_metric(
            Counter,
            "django_http_responses_total_by_charset",
            "Count of responses by charset.",
            ["charset"],
        )
        self.responses_streaming = self.register_metric(
            Counter,
            "django_http_responses_streaming_total",
            "Count of streaming responses.",
        )
        # Set in process_exception
        self.exceptions_by_type = self.register_metric(
            Counter,
            "django_http_exceptions_total_by_type",
            "Count of exceptions by object type.",
            ["type"],
        )
        self.exceptions_by_view = self.register_metric(
            Counter,
            "django_http_exceptions_total_by_view",
            "Count of exceptions by view.",
            ["view"],
        )


class PrometheusBeforeMiddleware(MiddlewareMixin):
    """Monitoring middleware that should run before other middlewares."""

    def __init__(self, get_response=None):
        super(PrometheusBeforeMiddleware, self).__init__(get_response)
        self.metrics = Metrics.get_instance()

    def process_request(self, request):
        self.metrics.requests_total.inc()
        request.prometheus_before_middleware_event = Time()

    def process_response(self, request, response):
        self.metrics.responses_total.inc()
        if hasattr(request, "prometheus_before_middleware_event"):
            self.metrics.requests_latency_before.observe(
                TimeSince(request.prometheus_before_middleware_event)
            )
        else:
            self.metrics.requests_unknown_latency_before.inc()
        return response


class PrometheusAfterMiddleware(MiddlewareMixin):

    """Monitoring middleware that should run after other middlewares."""

    def __init__(self, get_response=None):
        super(PrometheusAfterMiddleware, self).__init__(get_response)
        self.metrics = Metrics.get_instance()

    def _transport(self, request):
        return "https" if request.is_secure() else "http"

    def _method(self, request):
        m = request.method
        if m not in (
            "GET",
            "HEAD",
            "POST",
            "PUT",
            "DELETE",
            "TRACE",
            "OPTIONS",
            "CONNECT",
            "PATCH",
        ):
            return "<invalid method>"
        return m

    def process_request(self, request):
        transport = self._transport(request)
        method = self._method(request)
        self.metrics.requests_by_method.labels(method=method).inc()
        self.metrics.requests_by_transport.labels(transport=transport).inc()
        if request.is_ajax():
            self.metrics.requests_ajax.inc()
        content_length = int(request.META.get("CONTENT_LENGTH") or 0)
        self.metrics.requests_body_bytes.observe(content_length)
        request.prometheus_after_middleware_event = Time()

    def _get_view_name(self, request):
        view_name = "<unnamed view>"
        if hasattr(request, "resolver_match"):
            if request.resolver_match is not None:
                if request.resolver_match.view_name is not None:
                    view_name = request.resolver_match.view_name
        return view_name

    def process_view(self, request, view_func, *view_args, **view_kwargs):
        transport = self._transport(request)
        method = self._method(request)
        if hasattr(request, "resolver_match"):
            name = request.resolver_match.view_name or "<unnamed view>"
            self.metrics.requests_by_view_transport_method.labels(
                view=name, transport=transport, method=method
            ).inc()

    def process_template_response(self, request, response):
        if hasattr(response, "template_name"):
            self.metrics.responses_by_templatename.labels(
                templatename=str(response.template_name)
            ).inc()
        return response

    def process_response(self, request, response):
        method = self._method(request)
        name = self._get_view_name(request)
        status = str(response.status_code)
        self.metrics.responses_by_status.labels(status=status).inc()
        self.metrics.responses_by_status_view_method.labels(
            status=status, view=name, method=method
        ).inc()
        if hasattr(response, "charset"):
            self.metrics.responses_by_charset.labels(
                charset=str(response.charset)
            ).inc()
        if hasattr(response, "streaming") and response.streaming:
            self.metrics.responses_streaming.inc()
        if hasattr(response, "content"):
            self.metrics.responses_body_bytes.observe(len(response.content))
        if hasattr(request, "prometheus_after_middleware_event"):
            self.metrics.requests_latency_by_view_method.labels(
                view=self._get_view_name(request), method=request.method
            ).observe(TimeSince(request.prometheus_after_middleware_event))
        else:
            self.metrics.requests_unknown_latency.inc()
        return response

    def process_exception(self, request, exception):
        self.metrics.exceptions_by_type.labels(type=type(exception).__name__).inc()
        if hasattr(request, "resolver_match"):
            name = request.resolver_match.view_name or "<unnamed view>"
            self.metrics.exceptions_by_view.labels(view=name).inc()
        if hasattr(request, "prometheus_after_middleware_event"):
            self.metrics.requests_latency_by_view_method.labels(
                view=self._get_view_name(request), method=request.method
            ).observe(TimeSince(request.prometheus_after_middleware_event))
        else:
            self.metrics.requests_unknown_latency.inc()
