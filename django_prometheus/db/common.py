from django_prometheus.db import (
    connections_total, execute_total, execute_many_total, errors_total,
    connection_errors_total)


class ExceptionCounterByType(object):
    """A context manager that counts exceptions by type.

    Exceptions increment the provided counter, whose last label's name
    must match the `type_label` argument.

    In other words:

    c = Counter('http_request_exceptions_total', 'Counter of exceptions',
                ['method', 'type'])
    with ExceptionCounterByType(c, extra_labels={'method': 'GET'}):
        handle_get_request()
    """

    def __init__(self, counter, type_label='type', extra_labels=None):
        self._counter = counter
        self._type_label = type_label
        self._labels = extra_labels

    def __enter__(self):
        pass

    def __exit__(self, typ, value, traceback):
        if typ is not None:
            self._labels.update({self._type_label: typ.__name__})
            self._counter.labels(**self._labels).inc()


class DatabaseWrapperMixin(object):
    """Extends the DatabaseWrapper to count connections and cursors."""

    def get_new_connection(self, *args, **kwargs):
        connections_total.labels(self.alias, self.vendor).inc()
        try:
            return super(DatabaseWrapperMixin, self).get_new_connection(
                *args, **kwargs)
        except:
            connection_errors_total.labels(self.alias, self.vendor).inc()
            raise

    def create_cursor(self, name=None):
        return self.connection.cursor(factory=ExportingCursorWrapper(
            self.CURSOR_CLASS, self.alias, self.vendor))


def ExportingCursorWrapper(cursor_class, alias, vendor):
    """Returns a CursorWrapper class that knows its database's alias and
    vendor name.
    """

    class CursorWrapper(cursor_class):
        """Extends the base CursorWrapper to count events."""

        def execute(self, *args, **kwargs):
            execute_total.labels(alias, vendor).inc()
            with ExceptionCounterByType(errors_total, extra_labels={
                    'alias': alias, 'vendor': vendor}):
                return super(CursorWrapper, self).execute(*args, **kwargs)

        def executemany(self, query, param_list, *args, **kwargs):
            execute_total.labels(alias, vendor).inc(len(param_list))
            execute_many_total.labels(alias, vendor).inc(len(param_list))
            with ExceptionCounterByType(errors_total, extra_labels={
                    'alias': alias, 'vendor': vendor}):
                return super(CursorWrapper, self).executemany(
                    query, param_list, *args, **kwargs)
    return CursorWrapper
