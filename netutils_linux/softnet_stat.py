from random import randint
from optparse import Option
from base_top import BaseTop


class SoftnetStat:
    cpu = None
    total = None
    dropped = None
    time_squeeze = None
    cpu_collision = None
    received_rps = None

    def __init__(self, random=False):
        self.random = random

    def parse_string(self, row, cpu):
        row = [int('0x' + x, 16) for x in row.strip().split()]
        self.total, self.dropped, self.time_squeeze = row[0:3]
        self.cpu_collision = row[6]
        self.received_rps = row[7]
        self.cpu = cpu
        return self

    def parse_list(self, data):
        self.cpu, self.total, self.dropped, self.time_squeeze, self.cpu_collision, self.received_rps = data
        return self

    def __repr__(self):
        return "CPU: {0:2} total: {1:11} dropped: {2} time_squeeze: {3:4} cpu_collision: {4} received_rps: {5}" \
            .format(self.cpu, self.total, self.dropped, self.time_squeeze, self.cpu_collision, self.received_rps)

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
        return all([
            self.cpu == other.cpu,
            self.total == other.total,
            self.dropped == other.dropped,
            self.time_squeeze == other.time_squeeze,
            self.cpu_collision == other.cpu_collision,
            self.received_rps == other.received_rps,
        ])


class SoftnetStatTop(BaseTop):
    def __init__(self):
        BaseTop.__init__(self)
        specific_options = [
            Option('--softnet-stat-file', default='/proc/net/softnet_stat',
                   help='Option for testing on MacOS purpose.'),
        ]
        self.specific_options.extend(specific_options)

    def parse(self):
        with open(self.options.softnet_stat_file) as softnet_stat:
            data = softnet_stat.read().strip().split('\n')
            return [SoftnetStat(self.options.random).parse_string(row, cpu) for cpu, row in enumerate(data)]

    def eval(self):
        print self.current
        self.diff = [data - self.previous[cpu] for cpu, data in enumerate(self.current)]

    def __repr__(self):
        repr_source = self.diff if self.options.delta_mode else self.current
        return "\n".join(map(str, [self.header] + repr_source))


if __name__ == '__main__':
    SoftnetStatTop().run()
