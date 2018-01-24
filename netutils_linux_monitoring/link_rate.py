# coding=utf-8
from collections import namedtuple
from copy import deepcopy
from os import listdir, path
from random import randint
from re import match

from six import iteritems

from netutils_linux_monitoring.base_top import BaseTop
from netutils_linux_monitoring.colors import Color
from netutils_linux_monitoring.layout import make_table
from netutils_linux_monitoring.pci import PCI

Stat = namedtuple('Stat', ['filename', 'shortname'])


class LinkRateTop(BaseTop):
    """ Utility for monitoring network devices' pps and error rate """
    stats = [
        Stat('rx_packets', 'rx-packets'),
        Stat('rx_bytes', 'rx-bytes'),
        Stat('rx_errors', 'rx-errors'),
        Stat('rx_dropped', 'dropped'),
        Stat('rx_missed_errors', 'missed'),
        Stat('rx_fifo_errors', 'fifo'),
        Stat('rx_length_errors', 'length'),
        Stat('rx_over_errors', 'overrun'),
        Stat('rx_crc_errors', 'crc'),
        Stat('rx_frame_errors', 'frame'),
        Stat('tx_packets', 'tx-packets'),
        Stat('tx_bytes', 'tx-bytes'),
        Stat('tx_errors', 'tx-errors')
    ]
    align_map = None

    def __init__(self, pci=None):
        BaseTop.__init__(self)
        self.pci = pci

    def make_parser(self, parser=None):
        if not parser:
            parser = BaseTop.make_base_parser()
        parser.add_argument('--assert', '--assert-mode', default=False, dest='assert_mode',
                            help='Stops running after errors detected.')
        parser.add_argument('--dev', '--devices', default='', dest='devices',
                            help='Comma-separated list of devices to monitor.')
        parser.add_argument('--device-regex', default='^.*$',
                            help='Regex-mask for devices to monitor.')
        parser.add_argument('-s', '--simple', default=False, dest='simple_mode', action='store_true',
                            help='Hides different kinds of error, showing only general counters.')
        parser.add_argument('--rx', '--rx-only', dest='rx_only', default=False, action='store_true',
                            help='Hides tx-counters')
        parser.add_argument('--bits', default=False, action='store_true')
        parser.add_argument('--bytes', default=False, action='store_true')
        parser.add_argument('--kbits', default=False, action='store_true')
        parser.add_argument('--mbits', default=True, action='store_true')
        return parser

    def parse(self):
        return dict((dev, self.__parse_dev__(dev)) for dev in self.options.devices)

    def eval(self):
        self.diff = deepcopy(self.current)
        for dev, data in iteritems(self.current):
            for stat in self.stats:
                if self.options.random:
                    self.diff[dev][stat] = randint(0, 10000)
                else:
                    self.diff[dev][stat] = data[stat] - \
                                           self.previous[dev][stat]

    def make_header(self):
        return ['Device'] + [stat.shortname for stat in self.stats]

    @staticmethod
    def colorize_stat(stat, value):
        return Color.colorize(value, 1, 1) if 'errors' in stat.filename or 'dropped' in stat.filename else value

    def colorize_stats(self, dev, repr_source):
        return [self.colorize_stat(stat, repr_source[dev][stat]) for stat in self.stats]

    def make_rows(self):
        if not self.pci.devices:
            self.pci.devices = self.pci.node_dev_dict(self.options.devices, self.options.random)
        repr_source = self.repr_source()
        for dev in self.options.devices:
            dev_node = self.pci.devices.get(dev)
            dev_color = self.color.COLORS_NODE.get(dev_node)
            _dev = self.color.wrap(dev, dev_color)
            yield [_dev] + self.colorize_stats(dev, repr_source)

    def __repr__(self):
        table = make_table(self.make_header(), self.align_map, list(self.make_rows()))
        return self.__repr_table__(table)

    def __parse_dev__(self, dev):
        return dict((stat, self.__parse_dev_stat__(dev, stat)) for stat in self.stats)

    def __parse_dev_stat__(self, dev, stat):
        if self.options.random:
            return randint(1, 10000)
        filename = '/sys/class/net/{0}/statistics/{1}'.format(dev, stat.filename)
        with open(filename) as devfile:
            file_value = int(devfile.read().strip())
            if 'bytes' in stat.filename:
                return int(self.__repr_bytes(file_value))
            return file_value

    def __repr_bytes(self, value):
        if self.options.bytes:
            return value
        if self.options.bits:
            return value * 8
        elif self.options.kbits:
            return value * 8 / 1024
        return value * 8 / 1024 / 1024

    @staticmethod
    def __indent__(column, value, maxvalue=0):
        """ May be used for special indent for first column """
        return "{0:<14}".format(value) if column == maxvalue else "{0:>11}".format(value)

    def devices_list_validate(self, dev):
        return self.options.random or path.isdir('/sys/class/net/{0}'.format(dev))

    def devices_list_regex(self):
        """ Returns list of network devices matching --device-regex """
        net_dev_list = listdir('/sys/class/net/')
        return [dev for dev in net_dev_list if match(self.options.device_regex, dev)]

    def devices_list(self):
        """ Return list of network devices regarding --devices / --device-regex """
        if self.options.devices:
            devices = self.options.devices.split(',')
        else:
            devices = self.devices_list_regex()
        return [dev for dev in devices if self.devices_list_validate(dev)]

    def post_optparse(self):
        """ Asserting and applying parsing options """
        self.options.devices = self.devices_list()
        if not self.options.devices:
            raise ValueError("No devices've been specified")
        if self.options.rx_only:
            self.stats = [
                stat for stat in self.stats if stat.filename.startswith('rx')]
        if self.options.simple_mode:
            simple_stats = ('rx_packets', 'rx_bytes', 'rx_errors', 'tx_packets', 'tx_bytes', 'tx_errors')
            self.stats = [
                stat for stat in self.stats if stat.filename in simple_stats]
        self.unit_change()
        self.header = self.make_header()
        self.align_map = ['l'] + ['r'] * (len(self.header) - 1)
        if not self.pci:
            self.pci = PCI()
            self.pci.devices = self.pci.node_dev_dict(self.options.devices, self.options.random)
        self.color = Color(topology=None, enabled=self.options.color)

    def unit_change(self):
        if not any([self.options.bits, self.options.kbits, self.options.mbits]):
            return
        for i, stat in enumerate(self.stats):
            if 'bytes' not in stat.shortname:
                continue
            if self.options.bytes:
                continue
            elif self.options.bits:
                self.stats[i] = Stat(stat.filename, stat.shortname.replace('bytes', 'bits'))
            elif self.options.kbits:
                self.stats[i] = Stat(stat.filename, stat.shortname.replace('bytes', 'kbits'))
            elif self.options.mbits:
                self.stats[i] = Stat(stat.filename, stat.shortname.replace('bytes', 'mbits'))
