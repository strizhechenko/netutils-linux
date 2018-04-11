# coding=utf-8

# coding=utf-8

from copy import deepcopy
from random import randint
from subprocess import Popen, PIPE
from six.moves import xrange

from netutils_linux_monitoring.base_top import BaseTop
from netutils_linux_monitoring.layout import make_table


class AnyTop(BaseTop):
    """ Utility for monitoring hardware interrupts distribution """
    args = None
    diff_total = None

    def __int(self, line):
        return [self.int(item) for item in line.strip().split()]

    def main(self):
        parser = self.make_parser()
        self.options = parser.parse_args()
        self.run()

    def make_parser(self, parser=None):
        if not parser:
            parser = BaseTop.make_base_parser()
        parser.add_argument("cmd", nargs='+', type=str, action='store')
        return parser

    def parse(self):
        process = Popen(self.options.cmd, stdout=PIPE, stderr=PIPE)
        out, err = process.communicate()
        print(out.decode().split('\n'))
        process.kill()
        output = [self.__int(line.strip()) for line in out.decode().strip().split('\n')]
        for line in output:
            print(line)
        return output

    def eval(self):
        self.diff = deepcopy(self.current)
        for i, line in enumerate(self.diff):
            for j, column in enumerate(line):
                if isinstance(column, int):
                    if self.options.random:
                        self.diff[i][j] = randint(0, 10000)
                    else:
                        self.diff[i][j] = column - self.previous[i][j]
        self.diff_total = self.eval_diff_total()

    def make_rows(self):
        cpu_count = 0
        output_lines = list()
        if not self.diff_total:
            return ''
        for line in self.repr_source():
            if self.skip_zero_line(line):  # hiding useless data such a kind of interrupt etc
                continue
            else:  # make line with irq counters as compact as we can, it can be very long!
                line = line[1: cpu_count + 1] + [line[-1]]
            output_lines.append(line)
        return output_lines, cpu_count

    def __repr__(self):
        output_lines, cpu_count = self.make_rows()
        output_lines.insert(1, self.diff_total)
        output_lines.insert(2, [''] * (cpu_count + 1))
        table = make_table(output_lines[0], None, output_lines[1:])
        return self.__repr_table__(table)

    def eval_diff_total_column(self, column, cpucount):
        """ returns sum of all interrupts on given CPU """
        return sum(int(row[column]) for row in self.diff if len(row) > cpucount + 1)

    def eval_diff_total(self):
        """ returns list of interrupts' sums for each cpu """
        cpucount = len(self.diff[0]) - 1
        return [self.eval_diff_total_column(column, cpucount) for column in xrange(1, cpucount + 2)]

    def has_diff(self, row):
        """ detect if there were interrupts in this tick() on this IRQ """
        return any(x > self.options.delta_small_hide_limit for x in row if isinstance(x, int))

    def skip_zero_line(self, line):
        """ returns decision about hide not changed row in __repr__() """
        return self.options.delta_small_hide and not self.has_diff(line) and self.options.delta_mode
