# coding: utf-8
from six import iteritems

from netutils_linux_monitoring.base_top import BaseTop
from netutils_linux_monitoring.colors import Color
from netutils_linux_monitoring.layout import make_table


class Softirqs(BaseTop):
    """ Utility for monitoring software interrupts distribution """
    file_arg, file_value = '--softirqs-file', '/proc/softirqs'

    def __init__(self, topology=None):
        BaseTop.default_init(self, topology)

    def post_optparse(self):
        BaseTop.default_post_optparse(self)

    def parse(self):
        with open(self.options.softirqs_file) as softirq_file:
            metrics = [line.strip().split(':') for line in softirq_file.readlines() if ':' in line]
            return dict((k, [int(d) for d in v.strip().split()]) for k, v in metrics)

    def eval(self):
        self.diff = dict((key, self.list_diff(
            data, self.previous[key])) for key, data in iteritems(self.current))

    def __repr__(self):
        active_cpu_count = self.__active_cpu_count__(self.current)
        header = ['CPU', 'NET_RX', 'NET_TX']
        net_rx = self.repr_source().get('NET_RX')[:active_cpu_count]
        net_tx = self.repr_source().get('NET_TX')[:active_cpu_count]
        rows = [
            [
                self.color.wrap('CPU{0}'.format(n), self.color.colorize_cpu(n)),
                self.colorize_net_rx(v[0]),
                self.colorize_net_tx(v[1])
            ]
            for n, v in enumerate(zip(net_rx, net_tx))
        ]
        table = make_table(header, ['l', 'r', 'r'], rows)
        return self.__repr_table__(table)

    @staticmethod
    def colorize_net_rx(net_rx):
        """ :returns: highlighted by warning/error net_rx string """
        return Color.colorize(net_rx, 40000, 80000)

    @staticmethod
    def colorize_net_tx(net_tx):
        """ :returns: highlighted by warning/error net_tx string """
        return Color.colorize(net_tx, 20000, 30000)

    @staticmethod
    def __active_cpu_count__(data):
        return len([metric for metric in data.get('TIMER') if metric > 0])
