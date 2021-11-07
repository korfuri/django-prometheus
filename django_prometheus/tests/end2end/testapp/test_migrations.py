from unittest.mock import MagicMock

from django.test import SimpleTestCase

from django_prometheus.migrations import ExportMigrationsForDatabase
from django_prometheus.testutils import PrometheusTestCaseMixin


def M(metric_name):
    """Make a full metric name from a short metric name.

    This is just intended to help keep the lines shorter in test
    cases.
    """
    return "django_migrations_%s" % metric_name


class TestMigrations(PrometheusTestCaseMixin, SimpleTestCase):
    """Test migration counters."""

    def test_counters(self):
        executor = MagicMock()
        executor.migration_plan = MagicMock()
        executor.migration_plan.return_value = set()
        executor.loader.applied_migrations = {"a", "b", "c"}
        ExportMigrationsForDatabase("fakedb1", executor)
        self.assertEqual(executor.migration_plan.call_count, 1)
        executor.migration_plan = MagicMock()
        executor.migration_plan.return_value = {"a"}
        executor.loader.applied_migrations = {"b", "c"}
        ExportMigrationsForDatabase("fakedb2", executor)

        self.assertMetricEquals(3, M("applied_total"), connection="fakedb1")
        self.assertMetricEquals(0, M("unapplied_total"), connection="fakedb1")
        self.assertMetricEquals(2, M("applied_total"), connection="fakedb2")
        self.assertMetricEquals(1, M("unapplied_total"), connection="fakedb2")
