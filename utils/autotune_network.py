#!/usr/bin/env python
# coding: utf-8
# pylint: disable=C0111, C0103

import os
from netutils_linux_hardware.reader import Reader


def main():
    if os.path.isfile(os.path.join(os.getcwd(), 'lspci')):
        datadir = os.getcwd()
    else:
        test_dir = 'tests/autotune_network.tests'
        # test = '2xE5530.82576_and_82574L.l2_mixed.manual'
        test = '2xE5-2640.i350_and_82599ES.l2_mixed.masterconf'
        datadir = os.getenv('DATADIR', os.path.join(test_dir, test))
    print Reader(datadir)

if __name__ == '__main__':
    main()
