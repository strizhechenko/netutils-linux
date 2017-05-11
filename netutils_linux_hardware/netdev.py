# coding: utf-8
# pylint: disable=C0111, C0103

import os
from interrupts import IRQQueueCounter
from parsers import EthtoolBuffers, ReductorMirror, BrctlOutput, YAMLLike


class ReaderNet(object):

    netdevs = None

    def __init__(self, datadir, path):
        self.datadir = datadir
        self.path = path
        self.net_dev_list()

    def net_dev_list_bridge(self):
        bridges = self.path('brctl')
        return BrctlOutput().parse_file_safe(bridges)

    def net_dev_mirror_info(self):
        config_path = self.path('mirror_info.conf')
        return ReductorMirror().parse_file_safe(config_path)

    def net_dev_list_buffers(self):
        for netdev in self.netdevs:
            buffers_path = os.path.join(self.datadir, 'ethtool/g', netdev)
            self.netdevs[netdev]['buffers'] = EthtoolBuffers(
            ).parse_file_safe(buffers_path)

    def net_dev_list_drivers(self):
        keys_required = (
            'driver',
            'version',
        )
        for netdev in self.netdevs:
            driverfile = os.path.join(self.datadir, 'ethtool/i', netdev)
            driverdata = YAMLLike().parse_file_safe(driverfile)
            if driverdata:
                driverdata = dict((k, v) for k, v in driverdata.iteritems() if k in keys_required)
            else:
                driverdata = dict()
            self.netdevs[netdev]['driver'] = driverdata

    def net_dev_list(self):
        self.netdevs = self.net_dev_list_bridge() or self.net_dev_mirror_info()
        self.net_dev_list_buffers()
        self.net_dev_list_drivers()
        interrupts = self.path('interrupts')
        IRQQueueCounter().parse_file_safe(interrupts, netdevs=self.netdevs)
