# coding: utf-8
# pylint: disable=C0111, C0103

import os
from yaml import dump as dumps
from autotune_network_interrupts import IRQQueueCounter
from autotune_network_parsers import YAMLLike, CPULayout, EthtoolBuffers, ReductorMirror, BrctlOutput, DiskInfo, MemInfo


class Reader(object):

    def __init__(self, datadir):
        self.datadir = datadir
        self.gather_info()

    def __str__(self):
        return dumps(self.info, default_flow_style=False).strip()

    def path(self, filename):
        return os.path.join(self.datadir, filename)

    def net_dev_list_bridge(self):
        bridges = self.path('brctl')
        return BrctlOutput().parse_file_safe(bridges)

    def net_dev_mirror_info(self):
        config_path = self.path('mirror_info.conf')
        return ReductorMirror().parse_file_safe(config_path)

    def net_dev_list_buffers(self, netdevs):
        for netdev in netdevs:
            buffers_path = os.path.join(self.datadir, 'ethtool/g', netdev)
            netdevs[netdev]['buffers'] = EthtoolBuffers().parse_file_safe(buffers_path)

    def net_dev_list(self):
        netdevs = self.net_dev_list_bridge() or self.net_dev_mirror_info()
        self.net_dev_list_buffers(netdevs)
        interrupts = self.path('interrupts')
        IRQQueueCounter().parse_file_safe(interrupts, netdevs=netdevs)
        return netdevs

    def gather_info(self):

        self.info = {
            "cpu": {
                "info": YAMLLike().parse_file(self.path('lscpu_info')),
                "layout": CPULayout().parse_file(self.path('lscpu_layout')),
            },
            "net": self.net_dev_list(),
            "disk": DiskInfo().parse(self.path('disks_types'), self.path('lsblk_sizes'), self.path('lsblk_models')),
            "memory": MemInfo().parse_file(self.path('meminfo')),
        }
