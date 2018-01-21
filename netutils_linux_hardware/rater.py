# coding: utf-8

from netutils_linux_hardware.cpu import CPU
from netutils_linux_hardware.disk import Disk
from netutils_linux_hardware.folding import Folding
from netutils_linux_hardware.memory import Memory
from netutils_linux_hardware.net import Net
from netutils_linux_hardware.system import System
from netutils_linux_hardware.yaml_tools import dict2yaml


class Rater(object):
    """ Calculates rates for important system components """
    subsystems = {
        'net': Net,
        'cpu': CPU,
        'system': System,
        'memory': Memory,
        'disk': Disk,
    }

    def __init__(self, data, args):
        self.data = data
        self.args = args
        self.folding = Folding(args)
        self.info = None
        if self.data:
            self.rate()

    def rate(self):
        """ Rate every subsystem of the server """
        data = dict()
        for key, subsystem in self.subsystems.items():
            if getattr(self.args, key):
                data[key] = subsystem(self.data, self.folding).rate()
        self.info = self.folding.fold(data, Folding.SERVER)

    def __str__(self):
        return dict2yaml(self.info)
