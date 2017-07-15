import django
import psycopg2.extensions

from django_prometheus.db.common import DatabaseWrapperMixin, \
    ExportingCursorWrapper

if django.VERSION >= (1, 9):
    from django.db.backends.postgresql import base
else:
    from django.db.backends.postgresql_psycopg2 import base


class DatabaseFeatures(base.DatabaseFeatures):
    """Our database has the exact same features as the base one."""
    pass


class DatabaseWrapper(DatabaseWrapperMixin, base.DatabaseWrapper):
    def get_connection_params(self):
        conn_params = super(DatabaseWrapper, self).get_connection_params()
        conn_params['cursor_factory'] = ExportingCursorWrapper(
            psycopg2.extensions.cursor,
            self.alias,
            self.vendor,
        )
        return conn_params

    def create_cursor(self, name=None):
        # cursor_factory is a kwarg to connect() so restore create_cursor()'s
        # default behavior
        if django.VERSION >= (1, 11, 0):
            return base.DatabaseWrapper.create_cursor(self, name=name)
        else:
            return base.DatabaseWrapper.create_cursor(self)
