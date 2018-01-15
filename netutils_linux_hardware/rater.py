# coding: utf-8

import yaml

from netutils_linux_hardware.cpu import CPU
from netutils_linux_hardware.folding import Folding
from netutils_linux_hardware.grade import Grade
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
                data[key] = self.__rate(self.rate_netdev, 'net')
            elif key == 'cpu':
                data[key] = CPU(self.data).rate(self)
            elif key == 'memory':
                data[key] = self.rate_memory()
            elif key == 'disk':
                data[key] = self.__rate(self.rate_disk, 'disk')
            elif key == 'system':
                data[key] = self.rate_system()
        self.info = self.folding.fold(data, Folding.SERVER)

    def rate_memory_device(self, device):
        return self.folding.fold({
            'size': Grade.int(device.get('size', 0), 512, 8196),
            'type': Grade.known_values(device.get('type', 'RAM'), {
                'DDR1': 2,
                'DDR2': 3,
                'DDR3': 6,
                'DDR4': 10,
            }),
            'speed': Grade.int(device.get('speed', 0), 200, 4000),
        }, Folding.DEVICE)

    def rate_memory_devices(self, devices):
        if not devices:
            return 1
        return self.folding.fold(dict((handle, self.rate_memory_device(device))
                                      for handle, device in devices.items()),
                                 Folding.SUBSYSTEM)

    def rate_memory_size(self, size):
        return self.folding.fold({
            'MemTotal': Grade.int(size.get('MemTotal'), 2 * (1024 ** 2), 16 * (1024 ** 2)),
            'SwapTotal': Grade.int(size.get('SwapTotal'), 512 * 1024, 4 * (1024 ** 2)),
        }, Folding.DEVICE) if size else 1

    def rate_memory(self):
        meminfo = self.data.get('memory')
        if meminfo:
            return self.folding.fold({
                'devices': self.rate_memory_devices(meminfo.get('devices')),
                'size': self.rate_memory_size(meminfo.get('size')),
            }, Folding.SUBSYSTEM)

    def rate_system(self):
        cpuinfo = extract(self.data, ['cpu', 'info'])
        if cpuinfo:
            return self.folding.fold({
                'Hypervisor vendor': Grade.fact(cpuinfo.get('Hypervisor vendor'), False),
                'Virtualization type': Grade.fact(cpuinfo.get('Hypervisor vendor'), False),
            }, Folding.SUBSYSTEM)

    def rate_netdev(self, netdev):
        netdevinfo = extract(self.data, ['net', netdev])
        queues = sum(
            len(extract(netdevinfo, ['queues', x])) for x in ('rx', 'rxtx'))
        buffers = netdevinfo.get('buffers') or {}
        return self.folding.fold({
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
            'buffers': self.folding.fold({
                'cur': Grade.int(buffers.get('cur'), 256, 4096),
                'max': Grade.int(buffers.get('max'), 256, 4096),
            }, Folding.DEVICE)
        }, Folding.DEVICE)

    def rate_disk(self, disk):
        diskinfo = extract(self.data, ['disk', disk])
        return self.folding.fold({
            'type': Grade.str(diskinfo.get('type'), ['SDD'], ['HDD']),
            # 50Gb - good, 1Tb - good enough
            'size': Grade.int(diskinfo.get('size'), 50 * (1000 ** 3), 1000 ** 4),
        }, Folding.DEVICE)

    def __rate(self, func, key):
        items = self.data.get(key)
        return self.folding.fold(dict((item, func(item)) for item in items), Folding.SUBSYSTEM) if items else 1
