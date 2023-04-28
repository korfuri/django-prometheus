#!/usr/bin/env python
from django_prometheus.utils import PowersOf


class TestDjangoPrometheus:
    def testPowersOf(self):
        """Tests utils.PowersOf."""
        assert [0, 1, 2, 4, 8] == PowersOf(2, 4)
        assert [0, 3, 9, 27, 81, 243] == PowersOf(3, 5, lower=1)
        assert [1, 2, 4, 8] == PowersOf(2, 4, include_zero=False)
        assert [4, 8, 16, 32, 64, 128] == PowersOf(2, 6, lower=2, include_zero=False)
