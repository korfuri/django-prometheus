from django_prometheus.testutils import PrometheusTestCaseMixin
from django_prometheus.migrations import ExportMigrationsForDatabase
from django.test import TestCase
from unittest.mock import MagicMock


def M(metric_name):
    """Make a full metric name from a short metric name.

    This is just intended to help keep the lines shorter in test
    cases.
    """
    return 'django_migrations_%s' % metric_name


class TestMigrations(PrometheusTestCaseMixin, TestCase):
    """Test migration counters."""

    def test_counters(self):
        executor = MagicMock()
        executor.migration_plan = MagicMock()
        executor.migration_plan.return_value = set()
        executor.loader.applied_migrations = set(['a', 'b', 'c'])
        ExportMigrationsForDatabase('fakedb1', executor)
        executor.migration_plan.assert_called_once()
        executor.migration_plan = MagicMock()
        executor.migration_plan.return_value = set(['a'])
        executor.loader.applied_migrations = set(['b', 'c'])
        ExportMigrationsForDatabase('fakedb2', executor)

        self.assertMetricEquals(
            3, M('applied_total'), connection='fakedb1')
        self.assertMetricEquals(
            0, M('unapplied_total'), connection='fakedb1')
        self.assertMetricEquals(
            2, M('applied_total'), connection='fakedb2')
        self.assertMetricEquals(
            1, M('unapplied_total'), connection='fakedb2')
