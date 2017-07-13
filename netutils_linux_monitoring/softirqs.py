from six import iteritems

from netutils_linux_monitoring.base_top import BaseTop
from netutils_linux_monitoring.colors import wrap, cpu_color, colorize
from netutils_linux_monitoring.layout import make_table
from netutils_linux_monitoring.topology import Topology


class Softirqs(BaseTop):
    """ Utility for monitoring software interrupts distribution """

    def __init__(self, topology=None):
        BaseTop.__init__(self)
        self.topology = topology

    @staticmethod
    def make_parser(parser=None):
        if not parser:
            parser = BaseTop.make_parser()
        parser.add_argument('--softirqs-file', default='/proc/softirqs',
                            help='Option for testing on MacOS purpose.')
        return parser

    def post_optparse(self):
        if not self.topology:
            self.topology = Topology(fake=self.options.random)

    def parse(self):
        with open(self.options.softirqs_file) as softirq_file:
            metrics = [line.strip().split(':') for line in softirq_file.readlines() if ':' in line]
            return dict((k, [int(d) for d in v.strip().split()]) for k, v in metrics)

    def eval(self):
        self.diff = dict((key, self.list_diff(
            data, self.previous[key])) for key, data in iteritems(self.current))

    def __repr__(self):
        active_cpu_count = self.__active_cpu_count__(self.current)
        header = ["CPU", "NET_RX", "NET_TX"]
        net_rx = self.repr_source().get('NET_RX')[:active_cpu_count]
        net_tx = self.repr_source().get('NET_TX')[:active_cpu_count]
        rows = [
            [
                wrap("CPU{0}".format(n), cpu_color(n, self.topology)),
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
        return colorize(net_rx, 40000, 80000)

    @staticmethod
    def colorize_net_tx(net_tx):
        """ :returns: highlighted by warning/error net_tx string """
        return colorize(net_tx, 20000, 30000)

    @staticmethod
    def __active_cpu_count__(data):
        return len([metric for metric in data.get('TIMER') if metric > 0])
