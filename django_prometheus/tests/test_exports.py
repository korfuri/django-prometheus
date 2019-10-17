#!/usr/bin/env python
import socket
import unittest

from django_prometheus.exports import SetupPrometheusEndpointOnPortRange

from mock import patch, call, ANY, MagicMock


class ExportTest(unittest.TestCase):
    @patch('django_prometheus.exports.HTTPServer')
    def testPortRangeAvailable(self, httpserver_mock):
        """Test port range setup with an available port."""
        httpserver_mock.side_effect = [socket.error, MagicMock()]
        port_range = [8000, 8001]
        port_chosen = SetupPrometheusEndpointOnPortRange(port_range)

        expected_calls = [
            call(('', 8000), ANY),
            call(('', 8001), ANY),
        ]
        self.assertEqual(httpserver_mock.mock_calls, expected_calls)
        self.assertEqual(port_chosen, 8001)

    @patch('django_prometheus.exports.HTTPServer')
    def testPortRangeUnavailable(self, httpserver_mock):
        """Test port range setup with no available ports."""
        httpserver_mock.side_effect = [socket.error, socket.error]
        port_range = [8000, 8001]
        port_chosen = SetupPrometheusEndpointOnPortRange(port_range)

        expected_calls = [
            call(('', 8000), ANY),
            call(('', 8001), ANY),
        ]
        self.assertEqual(httpserver_mock.mock_calls, expected_calls)
        self.assertIsNone(port_chosen)


if __name__ == 'main':
    unittest.main()
