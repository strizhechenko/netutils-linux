# coding=utf-8

from netutils_linux_tuning.autorps import AutoRPS
from unittest import TestCase


class AutoRPSTests(TestCase):
    def test_cpus2mask_first_socket(self):
        expected = 'f0'
        cpus = [0, 1, 2, 3]
        self.assertEqual(AutoRPS.cpus2mask(cpus, 8), expected)

    def test_cpus2mask_second_socket(self):
        expected = 'f'
        cpus = [4, 5, 6, 7]
        self.assertEqual(AutoRPS.cpus2mask(cpus, 8), expected)

    def test_cpus2mask_all(self):
        expected = 'ff'
        cpus = list(range(8))
        self.assertEqual(AutoRPS.cpus2mask(cpus, 8), expected)
