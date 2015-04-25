from django_prometheus.db.common import DatabaseWrapperMixin
from django.db.backends.sqlite3 import base


class DatabaseFeatures(base.DatabaseFeatures):
    """Our database has the exact same features as the base one."""
    pass


class DatabaseWrapper(DatabaseWrapperMixin, base.DatabaseWrapper):
    CURSOR_CLASS = base.SQLiteCursorWrapper
