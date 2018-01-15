# coding=utf-8

from netutils_linux_hardware.grade import Grade
from netutils_linux_hardware.rater import extract
from netutils_linux_hardware.subsystem import Subsystem


class CPU(Subsystem):
    """ Everything about CPU: layouts, NUMA, HZ, L3, lscpu """

    def __init__(self, data=None):
        self.data = data

    def parse(self):
        pass

    def rate(self, rater):
        cpuinfo = extract(self.data, ['cpu', 'info'])
        if cpuinfo:
            return rater.folding.fold({
                'CPU MHz': Grade.int(cpuinfo.get('CPU MHz'), 2000, 4000),
                'BogoMIPS': Grade.int(cpuinfo.get('BogoMIPS'), 4000, 8000),
                'CPU(s)': Grade.int(cpuinfo.get('CPU(s)'), 2, 32),
                'Core(s) per socket': Grade.int(cpuinfo.get('Core(s) per socket'), 1, 2),
                'Socket(s)': Grade.int(cpuinfo.get('Socket(s)'), 1, 2),
                'Thread(s) per core': Grade.int(cpuinfo.get('Thread(s) per core'), 2, 1),
                'L3 cache': Grade.int(cpuinfo.get('L3 cache'), 1000, 30000),
                'Vendor ID': Grade.str(cpuinfo.get('Vendor ID'), good=['GenuineIntel']),
            }, rater.folding.SUBSYSTEM)
