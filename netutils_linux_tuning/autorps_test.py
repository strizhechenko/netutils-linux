# coding=utf-8

from unittest import TestCase

from netutils_linux_tuning.auto_softirq_tune import AutoRPS


class AutoRPSTests(TestCase):
    def test_all(self):
        dataset = {
            'f0': list(range(4)),
            'f': list(range(4, 8)),
            'ff': list(range(8))
        }
        for expected, cpus in dataset.items():
            self.assertEqual(AutoRPS.cpus2mask(cpus, 8), expected)
