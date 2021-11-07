from django.test import TestCase
from testapp.models import Dog, Lawn

from django_prometheus.testutils import PrometheusTestCaseMixin


def M(metric_name):
    """Make a full metric name from a short metric name.

    This is just intended to help keep the lines shorter in test
    cases.
    """
    return "django_model_%s" % metric_name


class TestModelMetrics(PrometheusTestCaseMixin, TestCase):
    """Test django_prometheus.models."""

    def test_counters(self):
        registry = self.saveRegistry()
        cool = Dog()
        cool.name = "Cool"
        cool.save()
        self.assertMetricDiff(registry, 1, M("inserts_total"), model="dog")

        elysees = Lawn()
        elysees.location = "Champs Elysees, Paris"
        elysees.save()
        self.assertMetricDiff(registry, 1, M("inserts_total"), model="lawn")
        self.assertMetricDiff(registry, 1, M("inserts_total"), model="dog")

        galli = Dog()
        galli.name = "Galli"
        galli.save()
        self.assertMetricDiff(registry, 2, M("inserts_total"), model="dog")

        cool.breed = "Wolfhound"
        self.assertMetricDiff(registry, 2, M("inserts_total"), model="dog")

        cool.save()
        self.assertMetricDiff(registry, 2, M("inserts_total"), model="dog")
        self.assertMetricDiff(registry, 1, M("updates_total"), model="dog")

        cool.age = 9
        cool.save()
        self.assertMetricDiff(registry, 2, M("updates_total"), model="dog")

        cool.delete()  # :(
        self.assertMetricDiff(registry, 2, M("inserts_total"), model="dog")
        self.assertMetricDiff(registry, 2, M("updates_total"), model="dog")
        self.assertMetricDiff(registry, 1, M("deletes_total"), model="dog")
