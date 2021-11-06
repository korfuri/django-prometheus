from django.test import SimpleTestCase, override_settings
from testapp.views import ObjectionException

from django_prometheus.testutils import PrometheusTestCaseMixin


def M(metric_name):
    """Makes a full metric name from a short metric name.

    This is just intended to help keep the lines shorter in test
    cases.
    """
    return "django_http_%s" % metric_name


def T(metric_name):
    """Makes a full metric name from a short metric name like M(metric_name)

    This method adds a '_total' postfix for metrics."""
    return "%s_total" % M(metric_name)


@override_settings(
    PROMETHEUS_LATENCY_BUCKETS=(0.05, 1.0, 2.0, 4.0, 5.0, 10.0, float("inf"))
)
class TestMiddlewareMetrics(PrometheusTestCaseMixin, SimpleTestCase):
    """Test django_prometheus.middleware.

    Note that counters related to exceptions can't be tested as
    Django's test Client only simulates requests and the exception
    handling flow is very different in that simulation.
    """

    def test_request_counters(self):
        registry = self.saveRegistry()
        self.client.get("/")
        self.client.get("/")
        self.client.get("/help")
        self.client.post("/", {"test": "data"})

        self.assertMetricDiff(registry, 4, M("requests_before_middlewares_total"))
        self.assertMetricDiff(registry, 4, M("responses_before_middlewares_total"))
        self.assertMetricDiff(registry, 3, T("requests_total_by_method"), method="GET")
        self.assertMetricDiff(registry, 1, T("requests_total_by_method"), method="POST")
        self.assertMetricDiff(
            registry, 4, T("requests_total_by_transport"), transport="http"
        )
        self.assertMetricDiff(
            registry,
            2,
            T("requests_total_by_view_transport_method"),
            view="testapp.views.index",
            transport="http",
            method="GET",
        )
        self.assertMetricDiff(
            registry,
            1,
            T("requests_total_by_view_transport_method"),
            view="testapp.views.help",
            transport="http",
            method="GET",
        )
        self.assertMetricDiff(
            registry,
            1,
            T("requests_total_by_view_transport_method"),
            view="testapp.views.index",
            transport="http",
            method="POST",
        )
        # We have 3 requests with no post body, and one with a few
        # bytes, but buckets are cumulative so that is 4 requests with
        # <=128 bytes bodies.
        self.assertMetricDiff(
            registry, 3, M("requests_body_total_bytes_bucket"), le="0.0"
        )
        self.assertMetricDiff(
            registry, 4, M("requests_body_total_bytes_bucket"), le="128.0"
        )
        self.assertMetricEquals(
            None, M("responses_total_by_templatename"), templatename="help.html"
        )
        self.assertMetricDiff(
            registry, 3, T("responses_total_by_templatename"), templatename="index.html"
        )
        self.assertMetricDiff(registry, 4, T("responses_total_by_status"), status="200")
        self.assertMetricDiff(
            registry, 0, M("responses_body_total_bytes_bucket"), le="0.0"
        )
        self.assertMetricDiff(
            registry, 3, M("responses_body_total_bytes_bucket"), le="128.0"
        )
        self.assertMetricDiff(
            registry, 4, M("responses_body_total_bytes_bucket"), le="8192.0"
        )
        self.assertMetricDiff(
            registry, 4, T("responses_total_by_charset"), charset="utf-8"
        )
        self.assertMetricDiff(registry, 0, M("responses_streaming_total"))

    def test_latency_histograms(self):
        # Caution: this test is timing-based. This is not ideal. It
        # runs slowly (each request to /slow takes at least .1 seconds
        # to complete), to eliminate flakiness we adjust the buckets used
        # in the test suite.

        registry = self.saveRegistry()

        # This always takes more than .1 second, so checking the lower
        # buckets is fine.
        self.client.get("/slow")
        self.assertMetricDiff(
            registry,
            0,
            M("requests_latency_seconds_by_view_method_bucket"),
            le="0.05",
            view="slow",
            method="GET",
        )
        self.assertMetricDiff(
            registry,
            1,
            M("requests_latency_seconds_by_view_method_bucket"),
            le="5.0",
            view="slow",
            method="GET",
        )

    def test_exception_latency_histograms(self):
        registry = self.saveRegistry()

        try:
            self.client.get("/objection")
        except ObjectionException:
            pass
        self.assertMetricDiff(
            registry,
            2,
            M("requests_latency_seconds_by_view_method_bucket"),
            le="2.0",
            view="testapp.views.objection",
            method="GET",
        )

    def test_streaming_responses(self):
        registry = self.saveRegistry()
        self.client.get("/")
        self.client.get("/file")
        self.assertMetricDiff(registry, 1, M("responses_streaming_total"))
        self.assertMetricDiff(
            registry, 1, M("responses_body_total_bytes_bucket"), le="+Inf"
        )
