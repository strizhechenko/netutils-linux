# coding: utf-8
# pylint: disable=C0111, C0103

from netutils_linux_hardware.cpu import CPU
from netutils_linux_hardware.disk import Disk
from netutils_linux_hardware.memory import Memory
from netutils_linux_hardware.net import Net
from netutils_linux_hardware.yaml_tools import dict2yaml


class Reader(object):
    """ Parser of raw saved data info dictionary """
    info = None
    subsystems = {
        'net': Net,
        'cpu': CPU,
        'memory': Memory,
        'disk': Disk,
    }

    def __init__(self, datadir, args):
        self.datadir = datadir
        self.args = args
        self.read()

    def __str__(self):
        return dict2yaml(self.info)

    def read(self):
        self.info = dict()
        for key, subsystem in self.subsystems.items():
            if getattr(self.args, key):
                self.info[key] = subsystem(datadir=self.datadir).parse()
        if not self.args.cpu and self.args.system:
            self.info['cpu'] = CPU(datadir=self.datadir).parse()
