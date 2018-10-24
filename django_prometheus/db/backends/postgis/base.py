import django
from django.db.backends.base.base import NO_DB_ALIAS
from django.db.backends.postgresql.base import (
    DatabaseWrapper as Psycopg2DatabaseWrapper,
)
import psycopg2.extensions

from django.contrib.gis.db.backends.postgis.features import DatabaseFeatures
from django.contrib.gis.db.backends.postgis.introspection import (
    PostGISIntrospection
)
from django.contrib.gis.db.backends.postgis.operations import PostGISOperations
from django.contrib.gis.db.backends.postgis.schema import PostGISSchemaEditor

from django_prometheus.db.common import DatabaseWrapperMixin, \
    ExportingCursorWrapper


class DatabaseWrapper(DatabaseWrapperMixin, Psycopg2DatabaseWrapper):
    SchemaEditorClass = PostGISSchemaEditor

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if kwargs.get('alias', '') != NO_DB_ALIAS:
            self.features = DatabaseFeatures(self)
            self.ops = PostGISOperations(self)
            self.introspection = PostGISIntrospection(self)

    def prepare_database(self):
        super().prepare_database()
        # Check that postgis extension is installed.
        with self.cursor() as cursor:
            cursor.execute("CREATE EXTENSION IF NOT EXISTS postgis")

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
            return Psycopg2DatabaseWrapper.create_cursor(self, name=name)
        else:
            return Psycopg2DatabaseWrapper.create_cursor(self)
