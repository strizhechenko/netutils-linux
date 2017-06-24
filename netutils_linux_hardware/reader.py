# coding: utf-8
# pylint: disable=C0111, C0103

import os
import yaml
from netutils_linux_hardware.parsers import YAMLLike, CPULayout, DiskInfo, MemInfo
from netutils_linux_hardware.netdev import ReaderNet


class Reader(object):

    info = None

    def __init__(self, datadir):
        self.datadir = datadir
        self.gather_info()

    def __str__(self):
        return yaml.dump(self.info, default_flow_style=False).strip()

    def path(self, filename):
        return os.path.join(self.datadir, filename)

    def gather_info(self):

        self.info = {
            "cpu": {
                "info": YAMLLike().parse_file_safe(self.path('lscpu_info')),
                "layout": CPULayout().parse_file_safe(self.path('lscpu_layout')),
            },
            "net": ReaderNet(self.datadir, self.path).netdevs,
            "disk": DiskInfo().parse(self.path('disks_types'), self.path('lsblk_sizes'), self.path('lsblk_models')),
            "memory": MemInfo().parse_file_safe(self.path('meminfo')),
        }
        for key in ('CPU MHz', 'BogoMIPS'):
            if self.info.get('cpu', {}).get('info', {}).get(key):
                self.info['cpu']['info'][key] = int(self.info['cpu']['info'][key])
