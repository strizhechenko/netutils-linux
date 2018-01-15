# coding=utf-8

from netutils_linux_hardware.grade import Grade
from netutils_linux_hardware.rater_math import extract
from netutils_linux_hardware.subsystem import Subsystem


class Net(Subsystem):
    """ Everything about Network: network devices' queues, driver, buffers """

    def parse(self):
        pass

    def rate(self):
        return self.map(self.__netdev, 'net')

    def __netdev(self, netdev):
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
            }, self.folding.DEVICE)
        }, self.folding.DEVICE)
