import sys

from django.core.management import call_command
from django.test import TestCase, override_settings

if sys.version_info[:2] >= (3, 0):
    from unittest.mock import patch, MagicMock
else:
    from mock import patch, MagicMock


class PushgatewayCommandTest(TestCase):

    GATEWAY_URL = 'https://example.local'
    GATEWAY_USER = 'foo'
    GATEWAY_PASSWORD = 'bar'

    @override_settings(PUSHGATEWAY_URL=GATEWAY_URL)
    @override_settings(PUSHGATEWAY_USER=GATEWAY_USER)
    @override_settings(PUSHGATEWAY_PASSWORD=GATEWAY_PASSWORD)
    @patch('django_prometheus.management.basic_auth_handler')
    def test_command_full(self, basic_auth_handler):
        call_command('pushgateway_job')
        args, kwargs = basic_auth_handler.call_args
        self.assertIn(
            kwargs['url'],
            self.GATEWAY_URL + '/metrics/job/my-cron-job',
        )
        self.assertIn('my_gauge{foo="bar"} 42.0', kwargs['data'])
        self.assertIn('my_counter_total 123.0', kwargs['data'])
        self.assertIn('job_last_duration_seconds', kwargs['data'])
        self.assertEqual(kwargs['username'], self.GATEWAY_USER)
        self.assertEqual(kwargs['password'], self.GATEWAY_PASSWORD)

    @override_settings(PUSHGATEWAY_URL=GATEWAY_URL)
    @override_settings(PUSHGATEWAY_USER=None)
    @override_settings(PUSHGATEWAY_PASSWORD=None)
    @patch('django_prometheus.management.default_handler')
    def test_command_no_auth(self, default_auth_handler):
        call_command('pushgateway_job')
        default_auth_handler.assert_called_once()
