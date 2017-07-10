#!/usr/bin/env python
# coding=utf-8

import unittest
from netutils_linux_tuning.rx_buffers import RxBuffersTune


class RxBuffersTuneTest(unittest.TestCase):
    """
    Just in-memory test of evaluation rx-buffer's size.
    No device's settings changed.
    """

    def setUp(self):
        self.rxbi = RxBuffersTune(['test'])
        self.default_upper_bound = 2048

    def test_4096(self):
        self.assertEqual(self.rxbi.eval_prefered_size(256, 4096, self.default_upper_bound), 2048)
        self.assertEqual(self.rxbi.eval_prefered_size(512, 4096, self.default_upper_bound), 2048)
        self.assertEqual(self.rxbi.eval_prefered_size(2048, 4096, self.default_upper_bound), 2048)
        self.assertEqual(self.rxbi.eval_prefered_size(3072, 4096, self.default_upper_bound), 3072)
        self.assertEqual(self.rxbi.eval_prefered_size(4096, 4096, self.default_upper_bound), 4096)

    def test_511(self):
        self.assertEqual(self.rxbi.eval_prefered_size(200, 511, self.default_upper_bound), 511)
        self.assertEqual(self.rxbi.eval_prefered_size(511, 511, self.default_upper_bound), 511)
        self.assertEqual(self.rxbi.eval_prefered_size(400, 511, self.default_upper_bound), 511)

    def test_8096(self):
        self.assertEqual(self.rxbi.eval_prefered_size(200, 8096, self.default_upper_bound), 2048)
        self.assertEqual(self.rxbi.eval_prefered_size(2048, 8096, self.default_upper_bound), 2048)
        self.assertEqual(self.rxbi.eval_prefered_size(3000, 8096, self.default_upper_bound), 3000)
        self.assertEqual(self.rxbi.eval_prefered_size(8096, 8096, self.default_upper_bound), 8096)


if __name__ == '__main__':
    unittest.main()
