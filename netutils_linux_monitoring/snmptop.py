# coding=utf-8

from six import print_

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

    def parse(self):
        with open(self.options.snmp_file) as file_fd:
            lines = [self.__int(line) for line in file_fd.readlines()]
        return {
            "IP": list(zip(lines[0][1:], lines[1][1:])),
            "ICMP": list(zip(lines[2][1:], lines[3][1:])),
            "TCP": list(zip(lines[6][3:], lines[7][1:])),
            "UDP": list(zip(lines[8][3:], lines[9][1:])),
        }

    def __repr__(self):
        return str(make_table(self.make_header(), self.make_align_map(), self.make_rows()))

    def make_header(self):
        return ['IP', '   ', 'TCP', '', 'UDP', ' ', 'ICMP', '  ']

    def make_rows(self):
        rows = []
        max_len = max(len(subdict) for subdict in snmp.values())
        for index in range(max_len):
            row = list()
            for proto in self.protos:
                if index >= len(snmp[proto]):
                    row.extend(['', ''])
                    continue
                row.extend([snmp[proto][index][0], snmp[proto][index][1]])
            rows.append(row)
        return rows

    def make_align_map(self):
        return ['l', 'r'] * len(self.protos)


if __name__ == '__main__':
    import sys

    sys.argv = [sys.argv[0], '--snmp-file=tests/proc_net_snmp/snmp1']
    top = SnmpTop()
    top.options = top.make_parser().parse_args()
    snmp = top.parse()
    print_(top)
