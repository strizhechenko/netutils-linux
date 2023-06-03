# coding=utf-8


from netutils_linux_hardware.grade import Grade
from netutils_linux_hardware.net_read import ReaderNet
from netutils_linux_hardware.rate_math import extract
from netutils_linux_hardware.subsystem import Subsystem


class Net(Subsystem):
    """ Everything about Network: network devices' queues, driver, buffers """

    def parse(self):
        return ReaderNet(self.datadir, self.path).netdevs

    def rate(self):
        return self.map(self.rate_device, 'net')

    def rate_device(self, netdev):
        netdevinfo = extract(self.data, ['net', netdev])
        queues = sum(len(extract(netdevinfo, ['queues', x])) for x in ('rx', 'rxtx'))
        queues_ethtool = self.rate_queue_ethtool(netdevinfo)
        buffers = netdevinfo.get('buffers') or {}
        return self.folding.fold({
            'queues': Grade.int(queues, 2, 8),
            'queues_ethtool': Grade.int(queues_ethtool, 2, 8),
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

    def rate_queue_ethtool(self, netdevinfo):
        # TODO: numa belonging
        # import json
        # print(json.dumps(netdevinfo, indent=2))
        # exit(0)
        queues_ethtool = netdevinfo['queues_ethtool']
        queues_type = 'rx'
        if not queues_ethtool:
            return 1
        if len(queues_ethtool.keys()) == 1:
            queues_type = list(queues_ethtool.keys())[0]
        cpu_count = len(self.data.get('cpu').get('layout'))
        # print(json.dumps(queues_ethtool, indent=2))
        # print(json.dumps(self.data.get('cpu').get('layout'), indent=4))
        queues_count = 0
        if queues_type == 'combined' or queues_type == 'rx':
            queues_count = queues_ethtool.get(queues_type).get('cur')
        return int(queues_count / cpu_count * 10)
