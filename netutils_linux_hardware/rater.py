# coding: utf-8

import yaml

from netutils_linux_hardware.cpu import CPU
from netutils_linux_hardware.disk import Disk
from netutils_linux_hardware.memory import Memory
from netutils_linux_hardware.folding import Folding
from netutils_linux_hardware.grade import Grade
from netutils_linux_hardware.net import Net
from netutils_linux_hardware.rater_math import extract


class Rater(object):
    """ Calculates rates for important system components """
    info = None
    avg = None
    keys = ('net', 'cpu', 'memory', 'system', 'disk')

    def __init__(self, data, args):
        self.data = data
        self.args = args
        self.folding = Folding(args)
        if self.data:
            self.rate()

    def __str__(self):
        return yaml.dump(self.info, default_flow_style=False).strip()

    def rate(self):
        data = dict()
        for key in self.keys:
            if not getattr(self.args, key):
                continue
            elif key == 'net':
                data[key] = Net(self.data, self.folding).rate()
            elif key == 'cpu':
                data[key] = CPU(self.data, self.folding).rate()
            elif key == 'memory':
                data[key] = Memory(self.data, self.folding).rate()
            elif key == 'disk':
                data[key] = Disk(self.data, self.folding).rate()
            elif key == 'system':
                data[key] = self.rate_system()
        self.info = self.folding.fold(data, Folding.SERVER)

    def rate_system(self):
        cpuinfo = extract(self.data, ['cpu', 'info'])
        if cpuinfo:
            return self.folding.fold({
                'Hypervisor vendor': Grade.fact(cpuinfo.get('Hypervisor vendor'), False),
                'Virtualization type': Grade.fact(cpuinfo.get('Hypervisor vendor'), False),
            }, Folding.SUBSYSTEM)
