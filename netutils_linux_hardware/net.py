# coding=utf-8
import os

from six import iteritems, print_

from netutils_linux_hardware.grade import Grade
from netutils_linux_hardware.parser import Parser
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


class ReductorMirror(Parser):
    @staticmethod
    def parse(text):
        lines = dict((line.split(' ', 1)) for line in text.strip().split('\n'))
        for netdev, conf in iteritems(lines):
            output = dict()
            output['conf'] = dict()
            output['conf']['vlan'], output['conf']['ip'] = conf.split()
            output['conf']['vlan'] = output['conf']['vlan'] != '-'
            if output['conf']['ip'] == '-':
                output['conf']['ip'] = ''
            lines[netdev] = output
        return lines


class NetdevParser(Parser):
    @staticmethod
    def parse(netdev_keys):
        """
        :param netdev_keys: list of device names
        :return: dict[device_name] = {'vlan': bool; 'ip': ''}
        """
        netdevs = dict()
        for key in netdev_keys:
            if key.count('.') == 1:
                dev, _ = key.split('.')
            elif key.count('.') == 0:
                dev = key
            else:
                print_('QinQ not supported yet. Device: {0}'.format(key))
                raise NotImplementedError
            netdevs[dev] = dict()
            netdevs[dev]['conf'] = {
                'vlan': key.count('.') == 1,
                'ip': '',
            }
        return netdevs


class BridgeOutput(NetdevParser):
    @staticmethod
    def parse(text):
        """ # 0 - id, 1 - dev, 2 - _, 3 - state, 4 - _, 5 - details, 6 - _, 7 - mtu, 8 - _, 9 - master
        :param text: # 3: eth1 state DOWN : <NO-CARRIER,BROADCAST,MULTICAST,UP> mtu 1500 master br1 state disabled
        :return: analyzed netdevs
        """
        __dev__ = 1
        netdevs_keys = [line.split()[__dev__] for line in text.strip().split('\n')]
        return NetdevParser.parse(netdevs_keys)


class EthtoolFiles(NetdevParser):
    def parse_file(self, filepath, **kwargs):
        return self.parse(os.listdir(filepath))


class EthtoolBuffers(Parser):
    @staticmethod
    def parse(text):
        buffers = [int(line.split()[1])
                   for line in text.strip().split('\n')
                   if line.startswith('RX:')]
        if buffers and len(buffers) == 2:
            return {
                'max': buffers[0],
                'cur': buffers[1],
            }
