# coding=utf-8

from random import randint
from copy import deepcopy
from optparse import Option
from netutils_linux_monitoring.base_top import BaseTop
from netutils_linux_monitoring.colors import colorize_cpu_list, colorize
from netutils_linux_monitoring.numa import Numa
from netutils_linux_monitoring.layout import make_table


class IrqTop(BaseTop):
    """ Utility for monitoring hardware interrupts distribution """
    diff_total = None
    irq_warning = 40000
    irq_error = 80000

    def __init__(self, numa=None):
        BaseTop.__init__(self)
        specific_options = [
            Option('--interrupts-file', default='/proc/interrupts',
                   help='Option for testing on MacOS purpose.')
        ]
        self.numa = numa
        self.specific_options.extend(specific_options)

    def post_optparse(self):
        if not self.numa:
            self.numa = Numa(fake=self.options.random)

    def __int(self, line):
        return [self.int(item) for item in line.strip().split()]

    def parse(self):
        with open(self.options.interrupts_file) as file_fd:
            return [self.__int(line) for line in file_fd.readlines()]

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

    @staticmethod
    def make_align_map(cpu_count):
        return ['r'] * cpu_count + ['l']

    def make_rows(self):
        cpu_count = 0
        output_lines = list()
        if not self.diff_total:
            return ""
        for line in self.repr_source():
            if line[0] == 'CPU0':
                cpu_count = len(line)
                line = colorize_cpu_list(line, self.numa) + ['']
            elif self.skip_zero_line(line):  # hiding useless data such a kind of interrupt etc
                continue
            else:  # make line with irq counters as compact as we can, it can be very long!
                line = line[1: cpu_count + 1] + [line[-1]]
            output_lines.append(line)
        return output_lines, cpu_count

    def __repr__(self):
        output_lines, cpu_count = self.make_rows()
        align_map = self.make_align_map(cpu_count)
        output_lines.insert(1, [colorize(irq, self.irq_warning, self.irq_error) for irq in self.diff_total] + ['TOTAL'])
        output_lines.insert(2, [''] * (cpu_count + 1))
        table = make_table(output_lines[0], align_map, output_lines[1:])
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
