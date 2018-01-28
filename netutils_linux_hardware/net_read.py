# coding=utf-8
import os

from six import iteritems

from netutils_linux_hardware.interrupts import IRQQueueCounter
from netutils_linux_hardware.parser import Parser, YAMLLike


class ReaderNet(object):
    """ Reading data about network from multiple sources and merging them for every network device """
    netdevs = None

    def __init__(self, datadir, path):
        self.datadir = datadir
        self.path = path
        self.net_dev_list()

    def max_cur_parse(self, ethtool_key, parser, output_key):
        for netdev in self.netdevs:
            file_path = os.path.join(self.datadir, 'ethtool/{0}'.format(ethtool_key), netdev)
            self.netdevs[netdev][output_key] = parser().parse_file_safe(file_path)

    def net_dev_list_queues(self):
        self.max_cur_parse('l', EthtoolQueues, 'queues_ethtool')
        IRQQueueCounter().parse_file_safe(self.path('interrupts'), netdevs=self.netdevs)

    def net_dev_list_buffers(self):
        self.max_cur_parse('g', EthtoolBuffers, 'buffers')

    def net_dev_list_drivers(self):
        keys_required = (
            'driver',
            'version',
        )
        for netdev in self.netdevs:
            driver_file = os.path.join(self.datadir, 'ethtool/i', netdev)
            driver_data = YAMLLike().parse_file_safe(driver_file) or dict()
            if driver_data:
                driver_data = dict((key, v) for key, v in iteritems(driver_data) if key in keys_required)
            self.netdevs[netdev]['driver'] = driver_data

    def net_dev_list_numa(self):
        for netdev in self.netdevs:
            numa_file = os.path.join(self.datadir, 'sys/class/net/', netdev, 'device/numa_node')
            self.netdevs[netdev]['numa_node'] = int(open(numa_file).read()) if os.path.exists(numa_file) else -1

    def net_dev_list(self):
        """
        Priority:
        1. mirror_info.conf (collected only in case of reductor (master conf))
        2. bridges output (collected only in case of reductor (manual conf))
        3. ethtool information (non reductor case)
        """
        self.netdevs = ReductorMirror().parse_file_safe(self.path('mirror_info.conf'))
        if not self.netdevs:
            self.netdevs = BridgeOutput().parse_file_safe(self.path('bridge_link'))
        if not self.netdevs:
            self.netdevs = EthtoolFiles().parse_file(self.path('ethtool/i'))
        if self.netdevs:
            self.net_dev_list_buffers()
            self.net_dev_list_drivers()
            self.net_dev_list_queues()
            self.net_dev_list_numa()


class NetdevClassificator(Parser):
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


class BridgeOutput(NetdevClassificator):
    @staticmethod
    def parse(text):
        """ # 0 - id, 1 - dev, 2 - _, 3 - state, 4 - _, 5 - details, 6 - _, 7 - mtu, 8 - _, 9 - master
        :param text: # 3: eth1 state DOWN : <NO-CARRIER,BROADCAST,MULTICAST,UP> mtu 1500 master br1 state disabled
        :return: analyzed netdevs
        """
        __dev__ = 1
        netdevs_keys = [line.split()[__dev__] for line in text.strip().split('\n')]
        return NetdevClassificator.parse(netdevs_keys)


class EthtoolFiles(NetdevClassificator):
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
