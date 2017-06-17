from optparse import Option
from netutils_linux_monitoring.base_top import BaseTop
from netutils_linux_monitoring.layout import make_table
from netutils_linux_monitoring.numa import Numa
from netutils_linux_monitoring.colors import wrap, cpu_color


class Softirqs(BaseTop):
    """ Utility for monitoring software interrupts distribution """

    net_rx_warning = 40000
    net_rx_error = 80000
    net_tx_warning = 20000
    net_tx_error = 30000

    def __init__(self, numa=None):
        BaseTop.__init__(self)
        specific_options = [
            Option('--softirqs-file', default='/proc/softirqs',
                   help='Option for testing on MacOS purpose.')
        ]
        self.numa = numa
        self.specific_options.extend(specific_options)

    def post_optparse(self):
        if not self.numa:
            self.numa = Numa(fake=self.options.random)

    def parse(self):
        with open(self.options.softirqs_file) as fd:
            metrics = [line.strip().split(':')
                       for line in fd.readlines() if ':' in line]
            return dict((k, map(int, v.strip().split())) for k, v in metrics)

    @staticmethod
    def __active_cpu_count__(data):
        return len([metric for metric in data.get('TIMER') if metric > 0])

    def eval(self):
        self.diff = dict((key, self.list_diff(
            data, self.previous[key])) for key, data in self.current.iteritems())

    def __repr__(self):
        active_cpu_count = self.__active_cpu_count__(self.current)
        header = ["CPU", "NET_RX", "NET_TX"]
        rows = [
            [wrap("CPU{0}".format(n), cpu_color(n, self.numa)), v[0], v[1]] for n, v in
            enumerate(zip(
                self.repr_source().get('NET_RX')[:active_cpu_count],
                self.repr_source().get('NET_TX')[:active_cpu_count]
            ))
        ]
        table = make_table(header, ['l', 'r', 'r'], rows)
        return self.__repr_table__(table)
