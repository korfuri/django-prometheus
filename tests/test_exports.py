#!/usr/bin/env python
from django_prometheus.exports import SetupPrometheusEndpointOnPortRange
import unittest


class ExportTest(unittest.TestCase):
    def testPortRange(self):
        port_range = [8000, 8001]
        SetupPrometheusEndpointOnPortRange(port_range)
        SetupPrometheusEndpointOnPortRange(port_range)

if __name__ == 'main':
    unittest.main()
