# coding: utf-8
import argparse

import yaml

from netutils_linux_hardware.assessor_math import extract
from netutils_linux_hardware.grade import Grade

FOLDING_NO = 0
FOLDING_DEVICE = 1
FOLDING_SUBSYSTEM = 2
FOLDING_SERVER = 3


class Assessor(object):
    """ Calculates rates for important system components """
    info = None
    avg = None

    def __init__(self, data, args):
        self.data = data
        self.args = args
        if self.data:
            self.assess()

    def fold(self, data, level):
        """ Схлапывает значения в дикте до среднего арифметического """
        if not data:
            return 1
        if self.args.folding < level:
            return data
        result = sum(data.values()) / len(data.keys())
        return result if level < FOLDING_SERVER else {'server': result}

    def __str__(self):
        return yaml.dump(self.info, default_flow_style=False).strip()

    def assess(self):
        self.info = self.fold({
            'net': self.__assess(self.assess_netdev, 'net'),
            'cpu': self.assess_cpu(),
            'memory': self.assess_memory(),
            'system': self.assess_system(),
            'disk': self.__assess(self.assess_disk, 'disk'),
        }, FOLDING_SERVER)

    def assess_cpu(self):
        cpuinfo = extract(self.data, ['cpu', 'info'])
        if cpuinfo:
            return self.fold({
                'CPU MHz': Grade.int(cpuinfo.get('CPU MHz'), 2000, 4000),
                'BogoMIPS': Grade.int(cpuinfo.get('BogoMIPS'), 4000, 8000),
                'CPU(s)': Grade.int(cpuinfo.get('CPU(s)'), 2, 32),
                'Core(s) per socket': Grade.int(cpuinfo.get('Core(s) per socket'), 1, 2),
                'Socket(s)': Grade.int(cpuinfo.get('Socket(s)'), 1, 2),
                'Thread(s) per core': Grade.int(cpuinfo.get('Thread(s) per core'), 2, 1),
                'L3 cache': Grade.int(cpuinfo.get('L3 cache'), 1000, 30000),
                'Vendor ID': Grade.str(cpuinfo.get('Vendor ID'), good=['GenuineIntel']),
            }, FOLDING_SUBSYSTEM)

    def assess_memory_device(self, device):
        return self.fold({
            'size': Grade.int(device.get('size', 0), 512, 8196),
            'type': Grade.known_values(device.get('type', 'RAM'), {
                'DDR1': 2,
                'DDR2': 3,
                'DDR3': 6,
                'DDR4': 10,
            }),
            'speed': Grade.int(device.get('speed', 0), 200, 4000),
        }, FOLDING_DEVICE)

    def assess_memory_devices(self, devices):
        if not devices:
            return 1
        return self.fold(dict((handle, self.assess_memory_device(device))
                              for handle, device in devices.items()),
                         FOLDING_SUBSYSTEM)

    def assess_memory_size(self, size):
        return self.fold({
            'MemTotal': Grade.int(size.get('MemTotal'), 2 * (1024 ** 2), 16 * (1024 ** 2)),
            'SwapTotal': Grade.int(size.get('SwapTotal'), 512 * 1024, 4 * (1024 ** 2)),
        }, FOLDING_DEVICE) if size else 1

    def assess_memory(self):
        meminfo = self.data.get('memory')
        if meminfo:
            return self.fold({
                'devices': self.assess_memory_devices(meminfo.get('devices')),
                'size': self.assess_memory_size(meminfo.get('size')),
            }, FOLDING_SUBSYSTEM)

    def assess_system(self):
        cpuinfo = extract(self.data, ['cpu', 'info'])
        if cpuinfo:
            return self.fold({
                'Hypervisor vendor': Grade.fact(cpuinfo.get('Hypervisor vendor'), False),
                'Virtualization type': Grade.fact(cpuinfo.get('Hypervisor vendor'), False),
            }, FOLDING_SUBSYSTEM)

    def assess_netdev(self, netdev):
        netdevinfo = extract(self.data, ['net', netdev])
        queues = sum(
            len(extract(netdevinfo, ['queues', x])) for x in ('rx', 'rxtx'))
        buffers = netdevinfo.get('buffers') or {}
        return self.fold({
            'queues': Grade.int(queues, 2, 8),
            'driver': {
                'mlx5_core': 10,  # 7500 mbit/s
                'mlx4_en': 9,  # 6500 mbit/s
                'i40e': 8,  # 6000 mbit/s
                'ixgbe': 7,  # 4000 mbit/s
                'igb': 6,  # 400 mbit/s
                'bnx2x': 4,  # 100 mbit/s
                'e1000e': 3,  # 80 mbit/s
                'e1000': 3,  # 50 mbit/s
                'r8169': 1, 'ATL1E': 1, '8139too': 1,  # real trash, you should never use it
            }.get(netdevinfo.get('driver').get('driver'), 2),
            'buffers': self.fold({
                'cur': Grade.int(buffers.get('cur'), 256, 4096),
                'max': Grade.int(buffers.get('max'), 256, 4096),
            }, FOLDING_DEVICE)
        }, FOLDING_DEVICE)

    def assess_disk(self, disk):
        diskinfo = extract(self.data, ['disk', disk])
        return self.fold({
            'type': Grade.str(diskinfo.get('type'), ['SDD'], ['HDD']),
            # 50Gb - good, 1Tb - good enough
            'size': Grade.int(diskinfo.get('size'), 50 * (1000 ** 3), 1000 ** 4),
        }, FOLDING_DEVICE)

    def __assess(self, func, key):
        items = self.data.get(key)
        return self.fold(dict((item, func(item)) for item in items), FOLDING_SUBSYSTEM) if items else 1

    def parse_args(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('-f', '--folding', action='count', help='-f - device, -ff - subsystem, -fff - server',
                            default=FOLDING_NO)
        return parser.parse_args()
