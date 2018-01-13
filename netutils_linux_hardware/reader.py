# coding: utf-8
# pylint: disable=C0111, C0103

import os

import yaml

from netutils_linux_hardware.netdev import ReaderNet
from netutils_linux_hardware.parsers import YAMLLike, CPULayout, DiskInfo, MemInfo, MemInfoDMI


class Reader(object):
    """ Parser of raw saved data info dictionary """
    info = None

    def __init__(self, datadir, args):
        self.datadir = datadir
        self.args = args
        self.gather_info()

    def __str__(self):
        return yaml.dump(self.info, default_flow_style=False).strip()

    def path(self, filename):
        return os.path.join(self.datadir, filename)

    def gather_info(self):
        self.info = dict()
        if self.args.cpu:
            self.info['cpu'] = {
                'info': YAMLLike(self.path('lscpu_info')).result,
                'layout': CPULayout(self.path('lscpu_layout')).result,
            }
        if self.args.net:
            self.info['net'] = ReaderNet(self.datadir, self.path).netdevs
        if self.args.disk:
            self.info['disk'] = DiskInfo().parse(
                self.path('disks_types'),
                self.path('lsblk_sizes'),
                self.path('lsblk_models')
            ),
        if self.args.memory:
            self.info['memory'] = {
                'size': MemInfo(self.path('meminfo')).result,
                'devices': MemInfoDMI(self.path('dmidecode')).result,
            }
        if self.info.get('cpu'):
            for key in ('CPU MHz', 'BogoMIPS'):
                if self.info.get('cpu', {}).get('info', {}).get(key):
                    self.info['cpu']['info'][key] = int(self.info['cpu']['info'][key])
