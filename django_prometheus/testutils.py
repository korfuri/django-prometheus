import copy
from prometheus_client import REGISTRY


METRIC_EQUALS_ERR_EXPLANATION = """
%s%s = %s, expected %s.
The values for %s are:
%s"""

METRIC_DIFF_ERR_EXPLANATION = """
%s%s changed by %f, expected %f.
Value before: %s
Value after: %s
"""

METRIC_COMPARE_ERR_EXPLANATION = """
The change in value of %s%s didn't match the predicate.
Value before: %s
Value after: %s
"""

METRIC_DIFF_ERR_NONE_EXPLANATION = """
%s%s was None after.
Value before: %s
Value after: %s
"""


class PrometheusTestCaseMixin(object):
    """A collection of utilities that make it easier to write test cases
    that interact with metrics.
    """

    def saveRegistry(self, registry=REGISTRY):
        """Freezes a registry. This lets a user test changes to a metric
        instead of testing the absolute value. A typical use case looks like:

          r = self.saveRegistry()
          doStuff()
          self.assertMetricDiff(r, 1, 'stuff_done_total')
        """
        return copy.deepcopy(list(registry.collect()))

    def getMetricFromFrozenRegistry(self, metric_name, frozen_registry,
                                    **labels):
        """Gets a single metric from a frozen registry."""
        for metric in frozen_registry:
            for n, l, value in metric.samples:
                if n == metric_name and l == labels:
                    return value

    def getMetric(self, metric_name, registry=REGISTRY, **labels):
        """Gets a single metric."""
        return self.getMetricFromFrozenRegistry(
            metric_name, registry.collect(), **labels)

    def getMetricVectorFromFrozenRegistry(self, metric_name, frozen_registry):
        """Like getMetricVector, but from a frozen registry."""
        output = []
        for metric in frozen_registry:
            for n, l, value in metric.samples:
                if n == metric_name:
                    output.append((l, value))
        return output

    def getMetricVector(self, metric_name, registry=REGISTRY):
        """Returns the values for all labels of a given metric.

        The result is returned as a list of (labels, value) tuples,
        where `labels` is a dict.

        This is quite a hack since it relies on the internal
        representation of the prometheus_client, and it should
        probably be provided as a function there instead.
        """
        return self.getMetricVectorFromFrozenRegistry(
            metric_name, registry.collect())

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

    def assertMetricEquals(self, expected_value, metric_name,
                           registry=REGISTRY, **labels):
        """Asserts that metric_name{**labels} == expected_value."""
        value = self.getMetric(metric_name, registry=registry, **labels)
        self.assertEqual(
            expected_value, value, METRIC_EQUALS_ERR_EXPLANATION % (
                metric_name, self.formatLabels(labels), value,
                expected_value, metric_name,
                self.formatVector(self.getMetricVector(metric_name))))

    def assertMetricDiff(self, frozen_registry, expected_diff,
                         metric_name, registry=REGISTRY, **labels):
        """Asserts that metric_name{**labels} changed by expected_diff between
        the frozen registry and now. A frozen registry can be obtained
        by calling saveRegistry, typically at the beginning of a test
        case.
        """
        saved_value = self.getMetricFromFrozenRegistry(
            metric_name, frozen_registry, **labels)
        current_value = self.getMetric(metric_name, registry=registry,
                                       **labels)
        self.assertFalse(
            current_value is None,
            METRIC_DIFF_ERR_NONE_EXPLANATION % (
                metric_name, self.formatLabels(labels),
                saved_value,
                current_value))
        diff = current_value - (saved_value or 0.0)
        self.assertEqual(
            expected_diff, diff,
            METRIC_DIFF_ERR_EXPLANATION % (
                metric_name, self.formatLabels(labels), diff, expected_diff,
                saved_value,
                current_value))

    def assertMetricCompare(self, frozen_registry, predicate,
                            metric_name, registry=REGISTRY, **labels):
        """Asserts that metric_name{**labels} changed according to a provided
        predicate function between the frozen registry and now. A
        frozen registry can be obtained by calling saveRegistry,
        typically at the beginning of a test case.
        """
        saved_value = self.getMetricFromFrozenRegistry(
            metric_name, frozen_registry, **labels)
        current_value = self.getMetric(metric_name, registry=registry,
                                       **labels)
        self.assertFalse(
            current_value is None,
            METRIC_DIFF_ERR_NONE_EXPLANATION % (
                metric_name, self.formatLabels(labels),
                saved_value,
                current_value))
        self.assertTrue(
            predicate(saved_value, current_value),
            METRIC_COMPARE_ERR_EXPLANATION % (
                metric_name, self.formatLabels(labels),
                saved_value,
                current_value))
