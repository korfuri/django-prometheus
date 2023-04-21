import psycopg2.extensions
from django.contrib.gis.db.backends.postgis import base

from django_prometheus.db.common import DatabaseWrapperMixin, ExportingCursorWrapper


class DatabaseWrapper(DatabaseWrapperMixin, base.DatabaseWrapper):
    def get_connection_params(self):
        conn_params = super().get_connection_params()
        conn_params["cursor_factory"] = ExportingCursorWrapper(
            psycopg2.extensions.cursor, "postgis", self.vendor
        )
        print(f"**** connection for PostGIS: {conn_params!r}")
        return conn_params

    def create_cursor(self, name=None):
        # cursor_factory is a kwarg to connect() so restore create_cursor()'s
        # default behavior
        print("**** Create cursur for PostGIS **** ")
        return base.DatabaseWrapper.create_cursor(self, name=name)
