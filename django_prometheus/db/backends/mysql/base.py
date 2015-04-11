from django_prometheus.db.common import get_current_exception_type
from django_prometheus.db import (
    connections_total, execute_total, execute_many_total, errors_total,
    connection_errors_total)
from django.db.backends.mysql import base


class DatabaseFeatures(base.DatabaseFeatures):
    """Our database has the exact same features as the base one."""
    pass


class DatabaseWrapper(base.DatabaseWrapper):
    """Extends the DatabaseWrapper to count connections and cursors."""

    def get_new_connection(self, *args, **kwargs):
        connections_total.labels(self.alias, self.vendor).inc()
        try:
            return super(DatabaseWrapper, self).get_new_connection(
                *args, **kwargs)
        except:
            connection_errors_total.labels(self.alias, self.vendor).inc()
            raise

    def create_cursor(self):
        cursor = self.connection.cursor()
        CursorWrapper = ExportingCursorWrapper(self.alias, self.vendor)
        return CursorWrapper(cursor)


def ExportingCursorWrapper(alias, vendor):
    """Returns a CursorWrapper class that knows its database's alias and
    vendor name.
    """

    class CursorWrapper(base.CursorWrapper):
        """Extends the base CursorWrapper to count events."""

        def execute(self, *args, **kwargs):
            execute_total.labels(alias, vendor).inc()
            try:
                return super(CursorWrapper, self).execute(*args, **kwargs)
            except:
                errors_total.labels(
                    alias, vendor, get_current_exception_type()).inc()
                raise

        def executemany(self, query, param_list, *args, **kwargs):
            execute_total.labels(alias, vendor).inc(len(param_list))
            execute_many_total.labels(alias, vendor).inc(len(param_list))
            try:
                return super(CursorWrapper, self).executemany(
                    query=query, param_list=param_list, *args, **kwargs)
            except:
                errors_total.labels(
                    alias, vendor, get_current_exception_type()).inc()
                raise
    return CursorWrapper
