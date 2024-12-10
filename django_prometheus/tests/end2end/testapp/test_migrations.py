from unittest.mock import patch

import pytest
from prometheus_client import CollectorRegistry

from django_prometheus.migrations import MigrationCollector



def M(metric_name):
    """Make a full metric name from a short metric name.

    This is just intended to help keep the lines shorter in test
    cases.
    """
    return "django_migrations_%s" % metric_name


@pytest.mark.django_db()
class TestMigrations:
    """Test migration counters."""

    @patch('django.db.migrations.executor.MigrationExecutor')
    def test_counters(self, MockMigrationExecutor):
        
        mock_executor = MockMigrationExecutor.return_value
        mock_executor.migration_plan.return_value = set()
        mock_executor.loader.applied_migrations = {"a", "b", "c"}
        
        test_registry = CollectorRegistry()
        collector = MigrationCollector()
        test_registry.register(collector)
        
        metrics = list(collector.collect())
        
        applied_metric = next((m for m in metrics if m.name == M("applied_total")), None)
        unapplied_metric = next((m for m in metrics if m.name == M("unapplied_total")), None)
        
        assert applied_metric.samples[0].value == 3
        assert applied_metric.samples[0].labels == {"connection": "default"}
        
        assert unapplied_metric.samples[0].value == 0
        assert unapplied_metric.samples[0].labels == {"connection": "default"}
        
        mock_executor.migration_plan.return_value = {"a"}
        mock_executor.loader.applied_migrations = {"b", "c"}
        
        metrics = list(collector.collect())
        
        applied_metric = next((m for m in metrics if m.name == M("applied_total")), None)
        unapplied_metric = next((m for m in metrics if m.name == M("unapplied_total")), None)
        
        assert applied_metric.samples[0].value == 2
        assert applied_metric.samples[0].labels == {"connection": "default"}
        
        assert unapplied_metric.samples[0].value == 1
        assert unapplied_metric.samples[0].labels == {"connection": "default"}
