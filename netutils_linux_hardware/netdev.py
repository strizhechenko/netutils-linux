# coding: utf-8
# pylint: disable=C0111, C0103

import os
from six import iteritems
from netutils_linux_hardware.interrupts import IRQQueueCounter
from netutils_linux_hardware.parsers import EthtoolBuffers, ReductorMirror, BridgeOutput, YAMLLike, EthtoolFiles


class ReaderNet(object):
    netdevs = None

    def __init__(self, datadir, path):
        self.datadir = datadir
        self.path = path
        self.net_dev_list()

    def net_dev_mirror_info(self):
        return ReductorMirror().parse_file_safe(self.path('mirror_info.conf'))

    def net_dev_list_bridge(self):
        return BridgeOutput().parse_file_safe(self.path('bridge_link'))

    def net_dev_list_ethtool(self):
        return EthtoolFiles().parse_file_safe(self.path('ethtool/i'))

    def net_dev_list_buffers(self):
        for netdev in self.netdevs:
            buffers_path = os.path.join(self.datadir, 'ethtool/g', netdev)
            self.netdevs[netdev]['buffers'] = EthtoolBuffers().parse_file_safe(buffers_path)

    def net_dev_list_drivers(self):
        keys_required = (
            'driver',
            'version',
        )
        for netdev in self.netdevs:
            driverfile = os.path.join(self.datadir, 'ethtool/i', netdev)
            driverdata = YAMLLike().parse_file_safe(driverfile)
            if driverdata:
                driverdata = dict((key, v) for key, v in iteritems(driverdata) if key in keys_required)
            else:
                driverdata = dict()
            self.netdevs[netdev]['driver'] = driverdata

    def net_dev_list(self):
        """
        Priority:
        1. mirror_info.conf (collected only in case of reductor (master conf))
        2. bridges output (collected only in case of reductor (manual conf))
        3. ethtool information (non reductor case)
        """
        self.netdevs = self.net_dev_mirror_info() or self.net_dev_list_bridge() or self.net_dev_list_ethtool()
        if not self.netdevs:
            return
        self.net_dev_list_buffers()
        self.net_dev_list_drivers()
        interrupts = self.path('interrupts')
        IRQQueueCounter().parse_file_safe(interrupts, netdevs=self.netdevs)
