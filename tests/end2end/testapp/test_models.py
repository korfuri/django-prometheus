from django_prometheus.testutils import PrometheusTestCaseMixin
from django.test import TestCase
from testapp.models import Dog, Lawn


def M(metric_name):
    """Make a full metric name from a short metric name.

    This is just intended to help keep the lines shorter in test
    cases.
    """
    return 'django_model_%s' % metric_name


class TestModelMetrics(PrometheusTestCaseMixin, TestCase):
    """Test django_prometheus.models."""

    def setUp(self):
        pass

    def test_counters(self):
        cool = Dog()
        cool.name = 'Cool'
        cool.save()
        self.assertMetricEquals(
            1, M('inserts_total'), model='dog')

        elysees = Lawn()
        elysees.location = 'Champs Elysees, Paris'
        elysees.save()
        self.assertMetricEquals(
            1, M('inserts_total'), model='lawn')
        self.assertMetricEquals(
            1, M('inserts_total'), model='dog')

        galli = Dog()
        galli.name = 'Galli'
        galli.save()
        self.assertMetricEquals(
            2, M('inserts_total'), model='dog')

        cool.breed = 'Wolfhound'
        self.assertMetricEquals(
            2, M('inserts_total'), model='dog')

        cool.save()
        self.assertMetricEquals(
            2, M('inserts_total'), model='dog')
        self.assertMetricEquals(
            1, M('updates_total'), model='dog')

        cool.age = 9
        cool.save()
        self.assertMetricEquals(
            2, M('updates_total'), model='dog')

        cool.delete()  # :(
        self.assertMetricEquals(
            2, M('inserts_total'), model='dog')
        self.assertMetricEquals(
            2, M('updates_total'), model='dog')
        self.assertMetricEquals(
            1, M('deletes_total'), model='dog')
