# coding=utf-8
""" Tests for server-info's parsing subsystem """

from unittest import TestCase

from netutils_linux_hardware.disk import DiskInfo


class DiskInfoTests(TestCase):
    @staticmethod
    def test_xen():
        """ There was a problem with disks with empty model name """
        directory_xen = './tests/server-info-show.tests/xen.lsblk/'
        directory_hw = './tests/server-info-show.tests/1xE3-1271.I217_and_X710.L2_mixed.masterconf/'
        for directory in (directory_hw, directory_xen):
            DiskInfo().parse(directory + 'disks_types', directory + 'lsblk_sizes', directory + 'lsblk_models')
