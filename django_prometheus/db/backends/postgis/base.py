from django import VERSION
from django.contrib.gis.db.backends.postgis import base

from django_prometheus.db.common import DatabaseWrapperMixin, ExportingCursorWrapper

if VERSION < (4, 2):
    from psycopg2.extensions import cursor as cursor_cls
else:
    from django.db.backends.postgresql.base import Cursor as cursor_cls


class DatabaseWrapper(DatabaseWrapperMixin, base.DatabaseWrapper):
    def get_connection_params(self):
        conn_params = super().get_connection_params()
        conn_params["cursor_factory"] = ExportingCursorWrapper(cursor_cls, "postgis", self.vendor)
        return conn_params

    def create_cursor(self, name=None):
        # cursor_factory is a kwarg to connect() so restore create_cursor()'s
        # default behavior
        return base.DatabaseWrapper.create_cursor(self, name=name)
