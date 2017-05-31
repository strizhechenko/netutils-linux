#!/usr/bin/env python

import unittest
from netutils_linux_monitoring.softirqs import Softirqs


class SoftirqsTest(unittest.TestCase):

    def test_file2data(self):
        for cpu in ('dualcore', 'i7'):
            for i in xrange(1, 6):
                top = Softirqs()
                top.parse_options()
                top.options.softirqs_file = 'tests/softirqs/{0}/softirqs{1}'.format(cpu, i)
                self.assertIn('NET_RX', top.parse())

if __name__ == '__main__':
    unittest.main()
