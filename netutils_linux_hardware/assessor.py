import re
import yaml


def extract(dictionary, key_sequence):
    key_sequence.reverse()
    while dictionary and key_sequence:
        dictionary = dictionary.get(key_sequence.pop())
    return dictionary


class Assessor(object):
    info = None
    avg = None

    def __init__(self, data):
        self.data = data
        if self.data:
            self.assess()

    def __str__(self):
        return yaml.dump(self.info, default_flow_style=False).strip()

    @staticmethod
    def any2int(value):
        if isinstance(value, int):
            return value
        elif value is None:
            return 0
        elif isinstance(value, str):
            v = re.sub(r'[^0-9]', '', value)
            if v.isdigit():
                return int(v)
        elif isinstance(value, float):
            return int(value)
        return 0

    def grade_int(self, value, _min, _max, scale=10):
        value = self.any2int(value)
        return min(scale, max(1, int(1 + round((value - _min) * (scale - 1.) / (_max - _min)))))

    @staticmethod
    def grade_str(value, good=None, bad=None):
        if bad and value in bad:
            return 1
        if good and value in good:
            return 10
        return 2

    @staticmethod
    def grade_fact(value, mode=False):
        return int((value is None) != mode) * 10 or 1

    def grade_list(self, value, minimum, maxmimum, scale=10):
        return self.grade_int(len(value), minimum, maxmimum, scale)

    def assess_netdev(self, netdev):
        netdevinfo = extract(self.data, ['net', netdev])
        queues = sum(
            len(extract(netdevinfo, ['queues', x])) for x in ('rx', 'rxtx'))
        buffers = netdevinfo.get('buffers') or {}
        return {
            'queues': self.grade_int(queues, 2, 8),
            'driver': {
                'mlx5_core': 10,                        # 7500 mbit/s
                'mlx4_en': 9,                           # 6500 mbit/s
                'i40e': 8,                              # 6000 mbit/s
                'ixgbe': 7,                             # 4000 mbit/s
                'igb': 6,                               # 400 mbit/s
                'bnx2x': 4,                             # 100 mbit/s
                'e1000e': 3,                            # 80 mbit/s
                'e1000': 3,                             # 50 mbit/s
                'r8169': 1, 'ATL1E': 1, '8139too': 1,   # real trash, you should never use it
            }.get(netdevinfo.get('driver').get('driver'), 2),
            'buffers': {
                'cur': self.grade_int(buffers.get('cur'), 256, 4096),
                'max': self.grade_int(buffers.get('max'), 256, 4096),
            },
        }

    def assess_netdevs(self):
        netdevs = self.data.get('net')
        if netdevs:
            return dict((netdev, self.assess_netdev(netdev)) for netdev in netdevs)

    def assess_cpu(self):
        cpuinfo = extract(self.data, ['cpu', 'info'])
        if cpuinfo:
            return {
                'CPU MHz': self.grade_int(cpuinfo.get('CPU MHz'), 2000, 4000),
                'BogoMIPS': self.grade_int(cpuinfo.get('BogoMIPS'), 4000, 8000),
                'CPU(s)': self.grade_int(cpuinfo.get('CPU(s)'), 2, 32),
                'Core(s) per socket': self.grade_int(cpuinfo.get('Core(s) per socket'), 1, 2),
                'Socket(s)': self.grade_int(cpuinfo.get('Socket(s)'), 1, 2),
                'Thread(s) per core': self.grade_int(cpuinfo.get('Thread(s) per core'), 2, 1),
                'L3 cache': self.grade_int(cpuinfo.get('L3 cache'), 1000, 30000),
                'Vendor ID': self.grade_str(cpuinfo.get('Vendor ID'), good=['GenuineIntel']),
            }

    def assess_memory(self):
        meminfo = self.data.get('memory')
        if meminfo:
            return {
                'MemTotal': self.grade_int(meminfo.get('MemTotal'), 2 * (1024 ** 2), 16 * (1024 ** 2)),
                'SwapTotal': self.grade_int(meminfo.get('SwapTotal'), 512 * 1024, 4 * (1024 ** 2)),
            }

    def assess_system(self):
        cpuinfo = extract(self.data, ['cpu', 'info'])
        if cpuinfo:
            return {
                'Hypervisor vendor': self.grade_fact(cpuinfo.get('Hypervisor vendor'), False),
                'Virtualization type': self.grade_fact(cpuinfo.get('Hypervisor vendor'), False),
            }

    def assess_disk(self, disk):
        diskinfo = extract(self.data, ['disk', disk])
        return {
            'type': self.grade_str(diskinfo.get('type'), ['SDD'], ['HDD']),
            # 50Gb - good, 1Tb - good enough
            'size': self.grade_int(diskinfo.get('size'), 50 * (1000 ** 3), 1000 ** 4),
        }

    def assess_disks(self):
        disks = self.data.get('disk')
        if disks:
            return dict((disk, self.assess_disk(disk)) for disk in disks)

    def assess(self):
        self.info = {
            'net': self.assess_netdevs(),
            'cpu': self.assess_cpu(),
            'memory': self.assess_memory(),
            'system': self.assess_system(),
            'disk': self.assess_disks(),
        }
