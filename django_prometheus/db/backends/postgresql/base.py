from django.db.backends.postgresql import base

from django_prometheus.db.backends.common import get_postgres_cursor_class
from django_prometheus.db.common import DatabaseWrapperMixin, ExportingCursorWrapper


class DatabaseWrapper(DatabaseWrapperMixin, base.DatabaseWrapper):
    def get_new_connection(self, *args, **kwargs):
        conn = super().get_new_connection(*args, **kwargs)
        conn.cursor_factory = ExportingCursorWrapper(
            conn.cursor_factory or get_postgres_cursor_class(), self.alias, self.vendor
        )
        return conn

    def create_cursor(self, name=None):
        # cursor_factory is a kwarg to connect() so restore create_cursor()'s
        # default behavior
        return base.DatabaseWrapper.create_cursor(self, name=name)
