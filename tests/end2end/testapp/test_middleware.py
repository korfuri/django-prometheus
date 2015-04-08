from django_prometheus.testutils import PrometheusTestCaseMixin
from django.test import TestCase


def M(metric_name):
    """Make a full metric name from a short metric name.

    This is just intended to help keep the lines shorter in test
    cases.
    """
    return 'django_http_%s' % metric_name


class TestMiddlewareMetrics(PrometheusTestCaseMixin, TestCase):
    """Test django_prometheus.middleware.

    Note that counters related to exceptions can't be tested as
    Django's test Client only simulates requests and the exception
    handling flow is very different in that simulation.
    """
    def test_request_counters(self):
        self.client.get('/')
        self.client.get('/')
        self.client.get('/help')
        self.client.post('/', {'test': 'data'})

        self.assertMetricEquals(4, M('requests_before_middlewares_total'))
        self.assertMetricEquals(4, M('responses_before_middlewares_total'))
        self.assertMetricEquals(
            3, M('requests_total_by_method'), method='GET')
        self.assertMetricEquals(
            1, M('requests_total_by_method'), method='POST')
        self.assertMetricEquals(
            4, M('requests_total_by_transport'), transport='http')
        self.assertMetricEquals(
            2, M('requests_total_by_view_transport_method'),
            view='testapp.views.index', transport='http', method='GET')
        self.assertMetricEquals(
            1, M('requests_total_by_view_transport_method'),
            view='testapp.views.help', transport='http', method='GET')
        self.assertMetricEquals(
            1, M('requests_total_by_view_transport_method'),
            view='testapp.views.index', transport='http', method='POST')
        # We have 3 requests with no post body, and one with a few
        # bytes, but buckets are cumulative so that is 4 requests with
        # <=128 bytes bodies.
        self.assertMetricEquals(
            3, M('requests_body_total_bytes_bucket'), le='0.0')
        self.assertMetricEquals(
            4, M('requests_body_total_bytes_bucket'), le='128.0')
        self.assertMetricEquals(
            None, M('responses_total_by_templatename'),
            templatename='help.html')
        self.assertMetricEquals(
            3, M('responses_total_by_templatename'),
            templatename='index.html')
        self.assertMetricEquals(
            4, M('responses_total_by_status'), status='200')
        self.assertMetricEquals(
            0, M('responses_body_total_bytes_bucket'), le='0.0')
        self.assertMetricEquals(
            3, M('responses_body_total_bytes_bucket'), le='128.0')
        self.assertMetricEquals(
            4, M('responses_body_total_bytes_bucket'), le='8192.0')
        self.assertMetricEquals(
            4, M('responses_total_by_charset'), charset='utf-8')
        self.assertMetricEquals(0, M('responses_streaming_total'))

    def test_latency_histograms(self):
        # Caution: this test is timing-based. This is not ideal. It
        # runs slowly (each request to /slow takes at least .1 seconds
        # to complete) and it may be flaky when run on very slow
        # systems.

        # This always takes more than .1 second, so checking the lower
        # buckets is fine.
        self.client.get('/slow')
        self.assertMetricEquals(
            0, M('requests_latency_seconds_bucket'), le='0.05')
        self.assertMetricEquals(
            1, M('requests_latency_seconds_bucket'), le='5.0')

        self.client.get('/')
        self.assertMetricEquals(
            2, M('requests_latency_seconds_bucket'), le='+Inf')
