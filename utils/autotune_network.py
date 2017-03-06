#!/usr/bin/env python
# coding: utf-8
# pylint: disable=C0111, C0103

import os
from autotune_network_reader import Reader


def main():
    if os.path.join(os.getcwd(), 'lspci'):
        datadir = os.getcwd()
    else:
        test_dir = 'tests/autotune_network.tests'
        test = '2xE5530.82576_and_82574L.l2_mixed.manual'
        datadir = os.getenv('DATADIR', os.path.join(test_dir, test))
    print Reader(datadir)

if __name__ == '__main__':
    main()
