#!/usr/bin/env python

import unittest

from six.moves import xrange

from netutils_linux_monitoring.numa import Numa
from netutils_linux_monitoring.softirqs import Softirqs


class SoftirqsTest(unittest.TestCase):

    def test_file2data(self):
        for cpu in ('dualcore', 'i7'):
            numa = Numa(fake=True)
            for i in xrange(1, 6):
                top = Softirqs(numa)
                top.parse_options()
                top.options.random = True
                top.options.softirqs_file = 'tests/softirqs/{0}/softirqs{1}'.format(cpu, i)
                self.assertTrue('NET_RX' in top.parse())


if __name__ == '__main__':
    unittest.main()
