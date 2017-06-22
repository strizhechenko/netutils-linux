#!/usr/bin/env python

import unittest

from netutils_linux_tuning.rx_buffers import RxBuffersIncreaser


class RxBuffersIncreaserTest(unittest.TestCase):
    """
    Just in-memory test of evaluation rx-buffer's size.
    No device's settings changed.
    """

    def setUp(self):
        self.rxbi = RxBuffersIncreaser()

    def test_4096(self):
        self.assertEqual(self.rxbi.determine(256, 4096), 2048)
        self.assertEqual(self.rxbi.determine(512, 4096), 2048)
        self.assertEqual(self.rxbi.determine(2048, 4096), 2048)
        self.assertEqual(self.rxbi.determine(3072, 4096), 3072)
        self.assertEqual(self.rxbi.determine(4096, 4096), 4096)

    def test_511(self):
        self.assertEqual(self.rxbi.determine(200, 511), 511)
        self.assertEqual(self.rxbi.determine(511, 511), 511)
        self.assertEqual(self.rxbi.determine(400, 511), 511)

    def test_8096(self):
        self.assertEqual(self.rxbi.determine(200, 8096), 2048)
        self.assertEqual(self.rxbi.determine(2048, 8096), 2048)
        self.assertEqual(self.rxbi.determine(3000, 8096), 3000)
        self.assertEqual(self.rxbi.determine(8096, 8096), 8096)


if __name__ == '__main__':
    unittest.main()
