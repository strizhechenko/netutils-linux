from random import randint
from optparse import Option
from base_top import BaseTop


class SoftnetStat:
    def __init__(self, row, cpu, random=False):
        row = [int('0x' + x, 16) for x in row.strip().split()]
        self.total, self.dropped, self.time_squeeze = row[0:3]
        self.cpu_collision = row[6]
        self.received_rps = row[7]
        self.cpu = cpu
        self.random = random

    def __repr__(self):
        return "CPU: {0:2} total: {1:11} dropped: {2} time_squeeze: {3:4} cpu_collision: {4} received_rps: {5}" \
            .format(self.cpu, self.total, self.dropped, self.time_squeeze, self.cpu_collision, self.received_rps)

    def __sub__(self, other):
        template = "CPU: {0:2} total: {1:8} dropped: {2} time_squeeze: {3} cpu_collision: {4} received_rps: {5}"
        if self.random:
            return template.format(self.cpu, randint(1, 100000), randint(0, 1), randint(0, 10), 0, randint(0, 5))
        return template \
            .format(self.cpu,
                    self.total - other.total,
                    self.dropped - other.dropped,
                    self.time_squeeze - other.time_squeeze,
                    self.cpu_collision - other.cpu_collision,
                    self.received_rps - other.received_rps)


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
            return [SoftnetStat(row, cpu, self.options.random) for cpu, row in enumerate(data)]

    def eval(self):
        self.diff = [data - self.previous[cpu] for cpu, data in enumerate(self.current)]

    def __repr__(self):
        repr_source = self.diff if self.options.delta_mode else self.current
        return "\n".join(map(str, [self.header] + repr_source))


if __name__ == '__main__':
    SoftnetStatTop().run()
