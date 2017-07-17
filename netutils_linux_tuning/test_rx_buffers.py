# coding=utf-8

import unittest
from netutils_linux_tuning.rx_buffers import RxBuffersTune


class RxBuffersTuneTest(unittest.TestCase):
    """
    Just in-memory test of evaluation rx-buffer's size.
    No device's settings changed.
    """
    dataset = {
        4096: [(256, 2048), (512, 2048), (2048, 2048), (3072, 3072), (4096, 4096)],
        511: ((200, 511), (511, 511), (400, 511)),
        8096: ((200, 2048), (2048, 2048), (3000, 3000), (8096, 8096))
    }

    def setUp(self):
        self.tune = RxBuffersTune(['test'])
        self.default_upper_bound = 2048

    def test_all(self):
        for max_buffer in self.dataset:
            for current, expected in self.dataset[max_buffer]:
                self.assertEqual(self.tune.eval_prefered_size(current, max_buffer, self.default_upper_bound), expected)


if __name__ == '__main__':
    unittest.main()
