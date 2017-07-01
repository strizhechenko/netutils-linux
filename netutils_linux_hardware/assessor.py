import yaml
from netutils_linux_hardware.assessor_math import extract
from netutils_linux_hardware.grade import Grade


class Assessor(object):
    info = None
    avg = None

    def __init__(self, data):
        self.data = data
        if self.data:
            self.assess()

    def __str__(self):
        return yaml.dump(self.info, default_flow_style=False).strip()

    def assess_netdev(self, netdev):
        netdevinfo = extract(self.data, ['net', netdev])
        queues = sum(
            len(extract(netdevinfo, ['queues', x])) for x in ('rx', 'rxtx'))
        buffers = netdevinfo.get('buffers') or {}
        return {
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
            'buffers': {
                'cur': Grade.int(buffers.get('cur'), 256, 4096),
                'max': Grade.int(buffers.get('max'), 256, 4096),
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
                'CPU MHz': Grade.int(cpuinfo.get('CPU MHz'), 2000, 4000),
                'BogoMIPS': Grade.int(cpuinfo.get('BogoMIPS'), 4000, 8000),
                'CPU(s)': Grade.int(cpuinfo.get('CPU(s)'), 2, 32),
                'Core(s) per socket': Grade.int(cpuinfo.get('Core(s) per socket'), 1, 2),
                'Socket(s)': Grade.int(cpuinfo.get('Socket(s)'), 1, 2),
                'Thread(s) per core': Grade.int(cpuinfo.get('Thread(s) per core'), 2, 1),
                'L3 cache': Grade.int(cpuinfo.get('L3 cache'), 1000, 30000),
                'Vendor ID': Grade.str(cpuinfo.get('Vendor ID'), good=['GenuineIntel']),
            }

    def assess_memory(self):
        meminfo = self.data.get('memory')
        if meminfo:
            return {
                'MemTotal': Grade.int(meminfo.get('MemTotal'), 2 * (1024 ** 2), 16 * (1024 ** 2)),
                'SwapTotal': Grade.int(meminfo.get('SwapTotal'), 512 * 1024, 4 * (1024 ** 2)),
            }

    def assess_system(self):
        cpuinfo = extract(self.data, ['cpu', 'info'])
        if cpuinfo:
            return {
                'Hypervisor vendor': Grade.fact(cpuinfo.get('Hypervisor vendor'), False),
                'Virtualization type': Grade.fact(cpuinfo.get('Hypervisor vendor'), False),
            }

    def assess_disk(self, disk):
        diskinfo = extract(self.data, ['disk', disk])
        return {
            'type': Grade.str(diskinfo.get('type'), ['SDD'], ['HDD']),
            # 50Gb - good, 1Tb - good enough
            'size': Grade.int(diskinfo.get('size'), 50 * (1000 ** 3), 1000 ** 4),
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
