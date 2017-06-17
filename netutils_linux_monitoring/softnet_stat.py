from random import randint
from optparse import Option
from netutils_linux_monitoring.base_top import BaseTop
from netutils_linux_monitoring.layout import make_table
from netutils_linux_monitoring.numa import Numa
from netutils_linux_monitoring.colors import cpu_color, wrap, colorize


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

    def sub(self, attr, other, _min, _max):
        return randint(_min, _max) if self.random else getattr(self, attr) - getattr(other, attr)

    def __sub__(self, other):
        return SoftnetStat().parse_list([
            self.cpu,
            self.sub('total', other, 1, 10000),
            self.sub('dropped', other, 0, 1),
            self.sub('time_squeeze', other, 0, 10),
            self.sub('cpu_collision', other, 0, 0),
            self.sub('received_rps', other, 0, 5),
        ])

    def __eq__(self, other):
        return all([getattr(self, attr) == getattr(other, attr) for attr in self.attributes])


class SoftnetStatTop(BaseTop):
    """ Utility for monitoring packets processing/errors distribution per CPU """

    align = ['l'] + ['r'] * 5
    total_warning, total_error = 300000, 900000
    dropped_warning = dropped_error = 1
    time_squeeze_warning, time_squeeze_error = 1, 300
    cpu_collision_warning, cpu_collision_error = 1, 1000

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
            colorize(stat.total, self.total_warning, self.total_error),
            colorize(stat.dropped, self.dropped_warning, self.dropped_error),
            colorize(stat.time_squeeze, self.time_squeeze_warning, self.time_squeeze_error),
            colorize(stat.cpu_collision, self.cpu_collision_warning, self.cpu_collision_error),
            stat.received_rps
        ]
            for stat in self.repr_source()
        ]

    def __repr__(self):
        table = make_table(self.make_header(), self.align, list(self.make_rows()))
        return self.__repr_table__(table)
