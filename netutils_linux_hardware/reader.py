# coding: utf-8
# pylint: disable=C0111, C0103

import os

import yaml

from netutils_linux_hardware.netdev import ReaderNet
from netutils_linux_hardware.parser import YAMLLike, CPULayout, DiskInfo, MemInfo, MemInfoDMI


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

    def read(self, func, filename):
        return func(self.path(filename)).result

    def __cpu(self):
        output = {
            'info': self.read(YAMLLike, 'lscpu_info'),
            'layout': self.read(CPULayout, 'lscpu_layout'),
        }
        for key in ('CPU MHz', 'BogoMIPS'):
            if output.get('info', {}).get(key):
                output['info'][key] = int(output['info'][key])
        return output

    def __memory(self):
        return {
            'size': self.read(MemInfo, 'meminfo'),
            'devices': self.read(MemInfoDMI, 'dmidecode'),
        }

    def gather_info(self):
        self.info = dict()
        if self.args.cpu or self.args.system:
            self.info['cpu'] = self.__cpu()
        if self.args.memory:
            self.info['memory'] = self.__memory()
        if self.args.net:
            self.info['net'] = ReaderNet(self.datadir, self.path).netdevs
        if self.args.disk:
            self.info['disk'] = DiskInfo().parse(
                self.path('disks_types'),
                self.path('lsblk_sizes'),
                self.path('lsblk_models')
            )
