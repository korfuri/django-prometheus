import django
from django_prometheus.testutils import PrometheusTestCaseMixin
from testapp.views import ObjectionException
from django.test import SimpleTestCase
import unittest


def M(metric_name):
    """Make a full metric name from a short metric name.

    This is just intended to help keep the lines shorter in test
    cases.
    """
    return 'django_http_%s' % metric_name


class TestMiddlewareMetrics(PrometheusTestCaseMixin, SimpleTestCase):
    """Test django_prometheus.middleware.

    Note that counters related to exceptions can't be tested as
    Django's test Client only simulates requests and the exception
    handling flow is very different in that simulation.
    """
    def test_request_counters(self):
        r = self.saveRegistry()
        self.client.get('/')
        self.client.get('/')
        self.client.get('/help')
        self.client.post('/', {'test': 'data'})

        self.assertMetricDiff(r, 4, M('requests_before_middlewares_total'))
        self.assertMetricDiff(r, 4, M('responses_before_middlewares_total'))
        self.assertMetricDiff(
            r, 3, M('requests_total_by_method'), method='GET')
        self.assertMetricDiff(
            r, 1, M('requests_total_by_method'), method='POST')
        self.assertMetricDiff(
            r, 4, M('requests_total_by_transport'), transport='http')
        self.assertMetricDiff(
            r, 2, M('requests_total_by_view_transport_method'),
            view='testapp.views.index', transport='http', method='GET')
        self.assertMetricDiff(
            r, 1, M('requests_total_by_view_transport_method'),
            view='testapp.views.help', transport='http', method='GET')
        self.assertMetricDiff(
            r, 1, M('requests_total_by_view_transport_method'),
            view='testapp.views.index', transport='http', method='POST')
        # We have 3 requests with no post body, and one with a few
        # bytes, but buckets are cumulative so that is 4 requests with
        # <=128 bytes bodies.
        self.assertMetricDiff(
            r, 3, M('requests_body_total_bytes_bucket'), le='0.0')
        self.assertMetricDiff(
            r, 4, M('requests_body_total_bytes_bucket'), le='128.0')
        self.assertMetricEquals(
            None, M('responses_total_by_templatename'),
            templatename='help.html')
        self.assertMetricDiff(
            r, 3, M('responses_total_by_templatename'),
            templatename='index.html')
        self.assertMetricDiff(
            r, 4, M('responses_total_by_status'), status='200')
        self.assertMetricDiff(
            r, 0, M('responses_body_total_bytes_bucket'), le='0.0')
        self.assertMetricDiff(
            r, 3, M('responses_body_total_bytes_bucket'), le='128.0')
        self.assertMetricDiff(
            r, 4, M('responses_body_total_bytes_bucket'), le='8192.0')
        self.assertMetricDiff(
            r, 4, M('responses_total_by_charset'), charset='utf-8')
        self.assertMetricDiff(r, 0, M('responses_streaming_total'))

    def test_latency_histograms(self):
        # Caution: this test is timing-based. This is not ideal. It
        # runs slowly (each request to /slow takes at least .1 seconds
        # to complete) and it may be flaky when run on very slow
        # systems.

        r = self.saveRegistry()

        # This always takes more than .1 second, so checking the lower
        # buckets is fine.
        self.client.get('/slow')
        self.assertMetricDiff(
            r, 0,
            M("requests_latency_seconds_by_view_method_bucket"),
            le='0.05', view="slow", method="GET")
        self.assertMetricDiff(
            r, 1,
            M("requests_latency_seconds_by_view_method_bucket"),
            le='5.0', view="slow", method="GET")

    def test_exception_latency_histograms(self):
        r = self.saveRegistry()

        try:
            self.client.get('/objection')
        except ObjectionException:
            pass
        self.assertMetricDiff(
            r, 2,
            M("requests_latency_seconds_by_view_method_bucket"),
            le='0.05', view="testapp.views.objection", method="GET")

    def test_streaming_responses(self):
        r = self.saveRegistry()
        self.client.get('/')
        self.client.get('/file')
        self.assertMetricDiff(r, 1, M('responses_streaming_total'))
        self.assertMetricDiff(
            r, 1,
            M('responses_body_total_bytes_bucket'), le='+Inf')
