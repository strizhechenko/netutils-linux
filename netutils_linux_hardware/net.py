# coding=utf-8
import os

from six import iteritems, print_

from netutils_linux_hardware.grade import Grade
from netutils_linux_hardware.interrupts import IRQQueueCounter
from netutils_linux_hardware.parser import Parser, YAMLLike
from netutils_linux_hardware.rate_math import extract
from netutils_linux_hardware.subsystem import Subsystem


class Net(Subsystem):
    """ Everything about Network: network devices' queues, driver, buffers """

    def parse(self):
        return ReaderNet(self.datadir, self.path).netdevs

    def rate(self):
        return self.map(self.__netdev, 'net')

    def __netdev(self, netdev):
        netdevinfo = extract(self.data, ['net', netdev])
        queues = sum(len(extract(netdevinfo, ['queues', x])) for x in ('rx', 'rxtx'))
        queues_ethtool = self.rate_queue_ethtool()
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

    def rate_queue_ethtool(self):


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


class EthtoolQueues(Parser):
    @staticmethod
    def parse(text):
        __queues = [int(line.split()[1]) for line in text.split('\n') if line.split()[1].isdigit()]
        if len(__queues) != 8:
            return
        queues = {
            'rx': {
                'max': __queues[0],
                'cur': __queues[4],
            },
            'combined': {
                'max': __queues[3],
                'cur': __queues[7],
            },
        }
        if queues['rx']['max'] == 0 and queues['combined']['max'] != 0:
            del queues['rx']
        return queues


class ReaderNet(object):
    """ Reading data about network from multiple sources and merging them for every network device """
    netdevs = None

    def __init__(self, datadir, path):
        self.datadir = datadir
        self.path = path
        self.net_dev_list()

    def net_dev_mirror_info(self):
        return ReductorMirror().parse_file_safe(self.path('mirror_info.conf'))

    def net_dev_list_bridge(self):
        return BridgeOutput().parse_file_safe(self.path('bridge_link'))

    def net_dev_list_ethtool(self):
        return EthtoolFiles().parse_file(self.path('ethtool/i'))

    def max_cur_parse(self, ethtool_key, parser, output_key):
        for netdev in self.netdevs:
            file_path = os.path.join(self.datadir, 'ethtool/{0}'.format(ethtool_key), netdev)
            self.netdevs[netdev][output_key] = parser().parse_file_safe(file_path)

    def net_dev_list_queues(self):
        self.max_cur_parse('l', EthtoolQueues, 'queues_ethtool')

    def net_dev_list_buffers(self):
        self.max_cur_parse('g', EthtoolBuffers, 'buffers')

    def net_dev_list_drivers(self):
        keys_required = (
            'driver',
            'version',
        )
        for netdev in self.netdevs:
            driver_file = os.path.join(self.datadir, 'ethtool/i', netdev)
            driver_data = YAMLLike().parse_file_safe(driver_file)
            if driver_data:
                driver_data = dict((key, v) for key, v in iteritems(driver_data) if key in keys_required)
            else:
                driver_data = dict()
            self.netdevs[netdev]['driver'] = driver_data

    def net_dev_list(self):
        """
        Priority:
        1. mirror_info.conf (collected only in case of reductor (master conf))
        2. bridges output (collected only in case of reductor (manual conf))
        3. ethtool information (non reductor case)
        """
        self.netdevs = self.net_dev_mirror_info() or self.net_dev_list_bridge() or self.net_dev_list_ethtool()
        if not self.netdevs:
            return
        self.net_dev_list_buffers()
        self.net_dev_list_drivers()
        self.net_dev_list_queues()
        interrupts = self.path('interrupts')
        IRQQueueCounter().parse_file_safe(interrupts, netdevs=self.netdevs)
