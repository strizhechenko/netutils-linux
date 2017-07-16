# coding=utf-8

from copy import deepcopy
from random import randint

from six import iteritems

from netutils_linux_monitoring.base_top import BaseTop
from netutils_linux_monitoring.layout import make_table


class SnmpTop(BaseTop):
    """ Utility for monitoring IP/TCP/UDP/ICMP parts of network stack based on /proc/net/snmp values """
    protos = ['IP', 'TCP', 'UDP', 'ICMP']
    file_arg, file_value = '--snmp-file', '/proc/net/snmp'

    def __int(self, line):
        return [self.int(item) for item in line.strip().split()]

    def eval(self):
        """ Evaluates difference between snmp metrics """
        self.diff = deepcopy(self.current)
        for proto, data in iteritems(self.diff):
            for i, metric in enumerate(data):
                _, value = metric
                if isinstance(value, int):
                    if self.options.random:
                        self.diff[proto][i][1] = randint(0, 1000)
                    else:
                        self.diff[proto][i][1] -= self.previous[proto][i][1]

    @staticmethod
    def __listify(lines, keys_id, values_id):
        """ :returns: list[list] = [[IpReceived, 23123], [IpSend, 231]] """
        return [list(tpl) for tpl in zip(lines[keys_id][1:], lines[values_id][1:])]

    def parse(self):
        """ :returns: dict[proto] = list[list[str(key), int(value)]] """
        with open(self.options.snmp_file) as file_fd:
            lines = [self.__int(line) for line in file_fd.readlines()]
        return {
            'IP': self.__listify(lines, 0, 1),
            'ICMP': self.__listify(lines, 2, 3),
            'TCP': self.__listify(lines, 6, 7),
            'UDP': self.__listify(lines, 8, 9)
        }

    def __repr__(self):
        table = make_table(self.make_header(), self.make_align_map(), self.make_rows())
        return self.__repr_table__(table)

    @staticmethod
    def make_header():
        """ :returns: header for prettytable output (provides unique invisible whitespace-headers)

        6, 5, 4 spaces are for column blinking avoidance.
        """
        return ['IP', ' ' * 6, 'TCP', ' ' * 5, 'UDP', ' ' * 4, 'ICMP', '']

    def make_rows(self):
        """ :returns: rows for prettytable output (filled with empty values) """
        rows = []
        repr_source = self.repr_source()
        max_len = max(len(subdict) for subdict in repr_source.values())
        for index in range(max_len):
            row = list()
            for proto in self.protos:
                if index >= len(repr_source[proto]):
                    row.extend(['', ''])
                    continue
                row.extend([repr_source[proto][index][0], repr_source[proto][index][1]])
            rows.append(row)
        return rows

    def make_align_map(self):
        """ :returns: align map for prettytable output (key <-, value -> for each proto """
        return ['l', 'r'] * len(self.protos)
