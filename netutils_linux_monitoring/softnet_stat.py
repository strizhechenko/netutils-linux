from random import randint
from optparse import Option
from netutils_linux_monitoring.base_top import BaseTop
from netutils_linux_monitoring.layout import make_table
from netutils_linux_monitoring.numa import Numa
from netutils_linux_monitoring.colors import cpu_color, wrap


class SoftnetStat(object):
    """ Representation for 1 CPU data in /proc/net/softnet_stat """
    cpu = None
    total = None
    dropped = None
    time_squeeze = None
    cpu_collision = None
    received_rps = None
    attributes = ['cpu', 'total', 'dropped', 'time_squeeze', 'cpu_collision', 'received_rps']

    def __init__(self, random=False):
        self.random = random

    def parse_string(self, row, cpu):
        """ Initialize SoftnetStat by string from /proc/net/softnet_stat """
        row = [int('0x' + x, 16) for x in row.strip().split()]
        self.total, self.dropped, self.time_squeeze = row[0:3]
        self.cpu_collision = row[6]
        self.received_rps = row[7]
        self.cpu = cpu
        return self

    def parse_list(self, data):
        """ Initialize SoftnetStat by list of integers """
        self.cpu, self.total, self.dropped, self.time_squeeze, self.cpu_collision, self.received_rps = data
        return self

    def __sub__(self, other):
        return SoftnetStat().parse_list([
            self.cpu,
            randint(1, 100000) if self.random else self.total - other.total,
            randint(0, 1) if self.random else self.dropped - other.dropped,
            randint(0, 10) if self.random else self.time_squeeze - other.time_squeeze,
            0 if self.random else self.cpu_collision - other.cpu_collision,
            randint(0, 5) if self.random else self.received_rps - other.received_rps
        ])

    def __eq__(self, other):
        return all([getattr(self, attr) == getattr(other, attr) for attr in self.attributes])


class SoftnetStatTop(BaseTop):
    """ Utility for monitoring packets processing/errors distribution per CPU """

    align = ['l'] + ['r'] * 5

    def __init__(self, numa=None):
        BaseTop.__init__(self)
        specific_options = [
            Option('--softnet-stat-file', default='/proc/net/softnet_stat',
                   help='Option for testing on MacOS purpose.'),
        ]
        self.numa = numa
        self.specific_options.extend(specific_options)

    def post_optparse(self):
        if not self.numa:
            self.numa = Numa(fake=self.options.random)

    def parse(self):
        with open(self.options.softnet_stat_file) as softnet_stat:
            data = enumerate(softnet_stat.read().strip().split('\n'))
            return [SoftnetStat(self.options.random).parse_string(row, cpu) for cpu, row in data]

    def eval(self):
        self.diff = [data - self.previous[cpu] for cpu, data in enumerate(self.current)]

    def make_header(self):
        return ["CPU", "total", "dropped", "time_squeeze", "cpu_collision", "received_rps"]

    def make_rows(self):
        return [[
            wrap("CPU{0}".format(stat.cpu), cpu_color(stat.cpu, self.numa)),
            stat.total, stat.dropped, stat.time_squeeze, stat.cpu_collision, stat.received_rps
        ]
            for stat in self.repr_source()
        ]

    def __repr__(self):
        table = make_table(self.make_header(), self.align, list(self.make_rows()))
        if self.options.clear:
            return BaseTop.header + str(table)
        return str(table)


if __name__ == '__main__':
    SoftnetStatTop().run()
