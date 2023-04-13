from django import VERSION

if VERSION < (4, 2):
    import psycopg2.extensions
    from django.contrib.gis.db.backends.postgis import base

    from django_prometheus.db.common import DatabaseWrapperMixin, ExportingCursorWrapper

    class DatabaseWrapper(DatabaseWrapperMixin, base.DatabaseWrapper):
        def get_connection_params(self):
            conn_params = super().get_connection_params()
            conn_params["cursor_factory"] = ExportingCursorWrapper(
                psycopg2.extensions.cursor, "postgis", self.vendor
            )
            return conn_params

        def create_cursor(self, name=None):
            # cursor_factory is a kwarg to connect() so restore create_cursor()'s
            # default behavior
            return base.DatabaseWrapper.create_cursor(self, name=name)

else:
    from django.contrib.gis.db.backends.postgis import base
    from django.db.backends.postgresql.base import Cursor
    from django_prometheus.db.common import DatabaseWrapperMixin, ExportingCursorWrapper

    class DatabaseWrapper(DatabaseWrapperMixin, base.DatabaseWrapper):
        def get_connection_params(self):
            conn_params = super().get_connection_params()
            conn_params["cursor_factory"] = ExportingCursorWrapper(
                Cursor, "postgis", self.vendor
            )
            return conn_params

        def create_cursor(self, name=None):
            # cursor_factory is a kwarg to connect() so restore create_cursor()'s
            # default behavior
            return base.DatabaseWrapper.create_cursor(self, name=name)
