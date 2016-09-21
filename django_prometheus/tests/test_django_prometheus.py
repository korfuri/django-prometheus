#!/usr/bin/env python
from django_prometheus.utils import PowersOf
import unittest


class DjangoPrometheusTest(unittest.TestCase):
    def testPowersOf(self):
        """Tests utils.PowersOf."""
        self.assertEqual(
            [0, 1, 2, 4, 8],
            PowersOf(2, 4))
        self.assertEqual(
            [0, 3, 9, 27, 81, 243],
            PowersOf(3, 5, lower=1))
        self.assertEqual(
            [1, 2, 4, 8],
            PowersOf(2, 4, include_zero=False))
        self.assertEqual(
            [4, 8, 16, 32, 64, 128],
            PowersOf(2, 6, lower=2, include_zero=False))


if __name__ == 'main':
    unittest.main()
