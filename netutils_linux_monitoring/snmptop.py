# coding=utf-8

import json
from six import print_
from netutils_linux_monitoring.base_top import BaseTop


class SnmpTop(BaseTop):
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
            lines = file_fd.readlines()
        return {
            "IP": dict(zip(lines[0].split()[1:], lines[1].split()[1:])),
            "ICMP": dict(zip(lines[2].split()[1:], lines[3].split()[1:])),
            "TCP": dict(zip(lines[6].split()[3:], lines[7].split()[1:])),
            "UDP": dict(zip(lines[8].split()[3:], lines[9].split()[1:])),
        }


    def __repr__(self):
        return json.dumps(self.parse(), indent=4)

if __name__ == '__main__':
    import sys
    sys.argv = [sys.argv[0], '--snmp-file=tests/proc_net_snmp/snmp1']
    top = SnmpTop()
    top.options = top.make_parser().parse_args()
    print_(top)
