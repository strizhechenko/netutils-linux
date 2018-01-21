# coding=utf-8

from netutils_linux_hardware.grade import Grade
from netutils_linux_hardware.parser import Parser, YAMLLike
from netutils_linux_hardware.rate_math import extract
from netutils_linux_hardware.subsystem import Subsystem


class CPU(Subsystem):
    """ Everything about CPU: layouts, NUMA, HZ, L3, lscpu """

    def rate(self):
        cpuinfo = extract(self.data, ['cpu', 'info'])
        if cpuinfo:  # None if no cpuinfo key
            return self.folding.fold({
                'CPU MHz': Grade.int(cpuinfo.get('CPU MHz'), 2000, 4000),
                'BogoMIPS': Grade.int(cpuinfo.get('BogoMIPS'), 4000, 8000),
                'CPU(s)': Grade.int(cpuinfo.get('CPU(s)'), 2, 32),
                'Core(s) per socket': Grade.int(cpuinfo.get('Core(s) per socket'), 1, 2),
                'Socket(s)': Grade.int(cpuinfo.get('Socket(s)'), 1, 2),
                'Thread(s) per core': Grade.int(cpuinfo.get('Thread(s) per core'), 2, 1),
                'L3 cache': Grade.int(cpuinfo.get('L3 cache'), 1000, 30000),
                'Vendor ID': Grade.str(cpuinfo.get('Vendor ID'), good=['GenuineIntel']),
            }, self.folding.SUBSYSTEM)

    def parse(self):
        output = {
            'info': self.read(YAMLLike, 'lscpu_info'),
            'layout': self.read(CPULayout, 'lscpu_layout'),
        }
        for key in ('CPU MHz', 'BogoMIPS'):
            if output.get('info', {}).get(key):
                output['info'][key] = int(output['info'][key])
        return output


class CPULayout(Parser):
    @staticmethod
    def parse(text):
        output = dict((line.strip().split())
                      for line in text.strip().split('\n'))
        if output.get('CPU'):
            del output['CPU']
        return output
