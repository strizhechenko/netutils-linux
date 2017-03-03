# coding: utf-8
# pylint: disable=C0111, C0103

import os
from yaml import dump as dumps
from autotune_network_interrupts import IRQQueueCounter
from autotune_network_parsers import YAMLLike, CPULayout, EthtoolBuffers, ReductorMirror, BrctlOutput


class Reader(object):

    def __init__(self, datadir):
        self.datadir = datadir
        self.gather_info()

    def __str__(self):
        return dumps(self.info, default_flow_style=False).strip()

    def net_dev_list_bridge(self):
        bridges = os.path.join(self.datadir, 'brctl')
        return BrctlOutput().parse_file_safe(bridges)

    def net_dev_mirror_info(self):
        config_path = os.path.join(self.datadir, 'mirror_info.conf')
        return ReductorMirror().parse_file_safe(config_path)

    def net_dev_list_buffers(self, netdevs):
        for netdev in netdevs:
            buffers_path = os.path.join(self.datadir, 'ethtool/g', netdev)
            netdevs[netdev]['buffers'] = EthtoolBuffers().parse_file_safe(buffers_path)

    def net_dev_list(self):
        netdevs = self.net_dev_list_bridge() or self.net_dev_mirror_info()
        self.net_dev_list_buffers(netdevs)
        interrupts = os.path.join(self.datadir, 'interrupts')
        IRQQueueCounter().parse_file_safe(interrupts, netdevs=netdevs)
        return netdevs

    def gather_info(self):
        self.info = {
            "cpu": {
                "info": YAMLLike().parse_file(os.path.join(self.datadir, 'lscpu_info')),
                "layout": CPULayout().parse_file(os.path.join(self.datadir, 'lscpu_layout')),
            },
            "net": self.net_dev_list(),
        }
