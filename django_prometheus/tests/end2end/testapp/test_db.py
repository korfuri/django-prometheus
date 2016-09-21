from unittest import skipUnless

from django_prometheus.testutils import PrometheusTestCaseMixin
from django.test import TestCase
from django.db import connections


@skipUnless(connections['test_db_1'].vendor == 'sqlite',
            "Skipped unless test_db_1 uses sqlite")
class TestDbMetrics(PrometheusTestCaseMixin, TestCase):
    """Test django_prometheus.db metrics.

    Note regarding the values of metrics: many tests interact with the
    database, and the test runner itself does. As such, tests that
    require that a metric has a specific value are at best very
    fragile. Consider asserting that the value exceeds a certain
    threshold, or check by how much it increased during the test.
    """
    def testConfigHasExpectedDatabases(self):
        """Not a real unit test: ensures that testapp.settings contains the
        databases this test expects."""
        self.assertTrue('default' in connections.databases.keys())
        self.assertTrue('test_db_1' in connections.databases.keys())
        self.assertTrue('test_db_2' in connections.databases.keys())

    def testCounters(self):
        cursor_db1 = connections['test_db_1'].cursor()
        cursor_db2 = connections['test_db_2'].cursor()
        cursor_db1.execute('SELECT 1')
        for _ in range(200):
            cursor_db2.execute('SELECT 2')
        cursor_db1.execute('SELECT 3')
        try:
            cursor_db1.execute('this is clearly not valid SQL')
        except:
            pass

        self.assertMetricEquals(
            1, 'django_db_errors_total',
            alias='test_db_1', vendor='sqlite', type='OperationalError')

        self.assertTrue(self.getMetric(
            'django_db_execute_total',
            alias='test_db_1', vendor='sqlite') > 0)
        self.assertTrue(self.getMetric(
            'django_db_execute_total',
            alias='test_db_2', vendor='sqlite') >= 200)

    def testExecuteMany(self):
        r = self.saveRegistry()
        cursor_db1 = connections['test_db_1'].cursor()
        cursor_db1.executemany(
            'INSERT INTO testapp_lawn(location) VALUES (?)', [
                ('Paris',), ('New York',), ('Berlin',), ('San Francisco',)])
        self.assertMetricDiff(r, 4, 'django_db_execute_many_total',
                              alias='test_db_1', vendor='sqlite')


@skipUnless('postgresql' in connections,
            "Skipped unless postgresql database is enabled")
class TestPostgresDbMetrics(PrometheusTestCaseMixin, TestCase):
    """Test django_prometheus.db metrics for postgres backend.

    Note regarding the values of metrics: many tests interact with the
    database, and the test runner itself does. As such, tests that
    require that a metric has a specific value are at best very
    fragile. Consider asserting that the value exceeds a certain
    threshold, or check by how much it increased during the test.
    """
    def testCounters(self):
        r = self.saveRegistry()
        cursor = connections['postgresql'].cursor()

        for _ in range(20):
            cursor.execute('SELECT 1')

        self.assertMetricCompare(r, lambda a, b: a + 20 <= b < a + 25,
                                 'django_db_execute_total',
                                 alias='postgresql', vendor='postgresql')


@skipUnless('mysql' in connections,
            "Skipped unless mysql database is enabled")
class TestMysDbMetrics(PrometheusTestCaseMixin, TestCase):
    """Test django_prometheus.db metrics for mys backend.

    Note regarding the values of metrics: many tests interact with the
    database, and the test runner itself does. As such, tests that
    require that a metric has a specific value are at best very
    fragile. Consider asserting that the value exceeds a certain
    threshold, or check by how much it increased during the test.
    """
    def testCounters(self):
        r = self.saveRegistry()
        cursor = connections['mysql'].cursor()

        for _ in range(20):
            cursor.execute('SELECT 1')

        self.assertMetricCompare(r, lambda a, b: a + 20 <= b < a + 25,
                                 'django_db_execute_total',
                                 alias='mysql', vendor='mysql')
