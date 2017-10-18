# coding=utf-8
""" Tests for server-info's parsing subsystem """

from unittest import TestCase

from netutils_linux_hardware.parsers import DiskInfo


class DiskInfoTests(TestCase):
    @staticmethod
    def test_xen():
        """ There was a problem with disks with empty model name """
        directory = './tests/server-info-show.tests/xen.lsblk/'
        disk_info = DiskInfo()
        disk_info.parse(directory + 'disks_types', directory + 'lsblk_sizes', directory + 'lsblk_models')
