from django.db import connections
from django.db.backends.dummy.base import DatabaseWrapper
from prometheus_client.core import GaugeMetricFamily, REGISTRY
from prometheus_client.registry import Collector

class MigrationCollector(Collector):
    def collect(self):
        from django.db.migrations.executor import MigrationExecutor

        applied_migrations = GaugeMetricFamily(
            "django_migrations_applied_total",
            "Count of applied migrations by database connection",
            labels=["connection"]
        )
        
        unapplied_migrations = GaugeMetricFamily(
            "django_migrations_unapplied_total",
            "Count of unapplied migrations by database connection",
            labels=["connection"]
        )

        if "default" in connections and isinstance(connections["default"], DatabaseWrapper):
        # This is the case where DATABASES = {} in the configuration,
        # i.e. the user is not using any databases. Django "helpfully"
        # adds a dummy database and then throws when you try to
        # actually use it. So we don't do anything, because trying to
        # export stats would crash the app on startup.
            return
        
        for alias in connections.databases:
            executor = MigrationExecutor(connections[alias])
            applied_migrations_count = len(executor.loader.applied_migrations)
            unapplied_migrations_count = len(executor.migration_plan(executor.loader.graph.leaf_nodes()))

            applied_migrations.add_metric([alias], applied_migrations_count)
            unapplied_migrations.add_metric([alias], unapplied_migrations_count)
        
        yield applied_migrations
        yield unapplied_migrations
