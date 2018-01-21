# coding=utf-8

from netutils_linux_hardware.grade import Grade
from netutils_linux_hardware.rate_math import extract
from netutils_linux_hardware.subsystem import Subsystem


class System(Subsystem):

    def rate(self):
        cpuinfo = extract(self.data, ['cpu', 'info'])
        if cpuinfo:
            return self.folding.fold({
                'Hypervisor vendor': Grade.fact(cpuinfo.get('Hypervisor vendor'), False),
                'Virtualization type': Grade.fact(cpuinfo.get('Hypervisor vendor'), False),
            }, self.folding.SUBSYSTEM)
