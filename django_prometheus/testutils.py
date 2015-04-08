from prometheus_client import REGISTRY


METRIC_EQUALS_ERR_EXPLANATION = """
%s%s = %s, expected %s.
The values for %s are:
%s"""


class PrometheusTestCaseMixin(object):
    """A collection of utilities that make it easier to write test cases
    that interact with metrics.
    """
    def setUp(self):
        self.clearRegistry()

    def clearRegistry(self):
        """Resets the values of all collectors in the global registry.

        This is so we can test the value of exported metrics in unit
        tests.

        This is quite a hack since it relies on the internal
        representation of the prometheus_client, and it should
        probably be provided as a function there instead.
        """
        with REGISTRY._lock:
            for c in REGISTRY._collectors:
                if hasattr(c, '_metrics'):
                    c._metrics = {}
                if hasattr(c, '_value'):
                    c._value = 0.0
                if hasattr(c, '_count'):
                    c._count = 0.0
                if hasattr(c, '_sum'):
                    c._sum = 0.0
                if hasattr(c, '_buckets'):
                    c._buckets = [0.0] * len(c._buckets)

    def getMetric(self, metric_name, **labels):
        return REGISTRY.get_sample_value(metric_name, labels=labels)

    def getMetricVector(self, metric_name):
        """Returns the values for all labels of a given metric.

        The result is returned as a list of (labels, value) tuples,
        where `labels` is a dict.

        This is quite a hack since it relies on the internal
        representation of the prometheus_client, and it should
        probably be provided as a function there instead.
        """
        all_metrics = REGISTRY.collect()
        output = []
        for metric in all_metrics:
            for n, l, value in metric._samples:
                if n == metric_name:
                    output.append((l, value))
        return output

    def formatLabels(self, labels):
        """Format a set of labels to Prometheus representation.

        In:
          {'method': 'GET', 'port': '80'}

        Out:
          '{method="GET",port="80"}'
        """
        return '{%s}' % ','.join([
            '%s="%s"' % (k, v) for k, v in labels.items()])

    def formatVector(self, vector):
        """Formats a list of (labels, value) where labels is a dict into a
        human-readable representation.
        """
        return '\n'.join([
            '%s = %s' % (self.formatLabels(labels), value)
            for labels, value in vector])

    def assertMetricEquals(self, expected_value, metric_name, **labels):
        """Asserts that metric_name{**labels} == expected_value."""
        value = self.getMetric(metric_name, **labels)
        self.assertEqual(
            expected_value, value, METRIC_EQUALS_ERR_EXPLANATION % (
                metric_name, self.formatLabels(labels), value,
                expected_value, metric_name,
                self.formatVector(self.getMetricVector(metric_name))))
