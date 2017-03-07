# coding: utf-8
# pylint: disable=C0111, C0103

import os
from autotune_network_interrupts import IRQQueueCounter
from autotune_network_parsers import EthtoolBuffers, ReductorMirror, BrctlOutput


class ReaderNet(object):

    def __init__(self, datadir, path):
        self.datadir = datadir
        self.path = path

    def net_dev_list_bridge(self):
        bridges = self.path('brctl')
        return BrctlOutput().parse_file_safe(bridges)

    def net_dev_mirror_info(self):
        config_path = self.path('mirror_info.conf')
        return ReductorMirror().parse_file_safe(config_path)

    def net_dev_list_buffers(self, netdevs):
        for netdev in netdevs:
            buffers_path = os.path.join(self.datadir, 'ethtool/g', netdev)
            netdevs[netdev]['buffers'] = EthtoolBuffers(
            ).parse_file_safe(buffers_path)

    def net_dev_list(self):
        netdevs = self.net_dev_list_bridge() or self.net_dev_mirror_info()
        self.net_dev_list_buffers(netdevs)
        interrupts = self.path('interrupts')
        IRQQueueCounter().parse_file_safe(interrupts, netdevs=netdevs)
        return netdevs
