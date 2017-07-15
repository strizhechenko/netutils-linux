# coding=utf-8

from random import randint
from six import print_, iteritems
from copy import deepcopy
from netutils_linux_monitoring.base_top import BaseTop
from netutils_linux_monitoring.layout import make_table


class SnmpTop(BaseTop):
    protos = ['IP', 'TCP', 'UDP', 'ICMP']

    @staticmethod
    def make_parser(parser=None):
        if not parser:
            parser = BaseTop.make_parser()
        parser.add_argument('--snmp-file', default='/proc/net/snmp',
                            help='Option for testing on MacOS purpose.')
        return parser

    def __int(self, line):
        return [self.int(item) for item in line.strip().split()]

    def eval(self):
        self.diff = deepcopy(self.current)
        for proto, data in iteritems(self.diff):
            for n, metric in enumerate(data):
                key, value = metric
                if isinstance(value, int):
                    if self.options.random:
                        self.diff[proto][n][1] = randint(0, 1000)
                    else:
                        self.diff[proto][n][1] -= self.previous[proto][n][1]

    def parse(self):
        with open(self.options.snmp_file) as file_fd:
            lines = [self.__int(line) for line in file_fd.readlines()]
        return {
            "IP": list(map(list, list(zip(lines[0][1:], lines[1][1:])))),
            "ICMP": list(map(list, list(zip(lines[2][1:], lines[3][1:])))),
            "TCP": list(map(list, list(zip(lines[6][3:], lines[7][1:])))),
            "UDP": list(map(list, list(zip(lines[8][3:], lines[9][1:])))),
        }

    def __repr__(self):
        return str(make_table(self.make_header(), self.make_align_map(), self.make_rows()))

    def make_header(self):
        return ['IP', '   ', 'TCP', '', 'UDP', ' ', 'ICMP', '  ']

    def make_rows(self):
        rows = []
        max_len = max(len(subdict) for subdict in self.diff.values())
        for index in range(max_len):
            row = list()
            for proto in self.protos:
                if index >= len(self.diff[proto]):
                    row.extend(['', ''])
                    continue
                row.extend([self.diff[proto][index][0], self.diff[proto][index][1]])
            rows.append(row)
        return rows

    def make_align_map(self):
        return ['l', 'r'] * len(self.protos)


if __name__ == '__main__':
    top = SnmpTop()
    top.options = top.make_parser().parse_args()
    top.run()
