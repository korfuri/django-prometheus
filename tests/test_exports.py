#!/usr/bin/env python
import socket
import unittest

from mock import patch, call, ANY, MagicMock

from django_prometheus.exports import SetupPrometheusEndpointOnPortRange


class ExportTest(unittest.TestCase):
    @patch('django_prometheus.exports.HTTPServer')
    def testPortRange(self, httpserver_mock):
        httpserver_mock.side_effect = [socket.error, MagicMock()]
        port_range = [8000, 8001]
        SetupPrometheusEndpointOnPortRange(port_range)

        expected_calls = [
            call(('', 8000), ANY),
            call(('', 8001), ANY),
        ]
        self.assertEqual(httpserver_mock.mock_calls, expected_calls)


if __name__ == 'main':
    unittest.main()
