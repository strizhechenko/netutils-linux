# coding=utf-8

from copy import deepcopy
from random import randint

from six.moves import xrange

from netutils_linux_monitoring.base_top import BaseTop
from netutils_linux_monitoring.colors import Color
from netutils_linux_monitoring.layout import make_table


class IrqTop(BaseTop):
    """ Utility for monitoring hardware interrupts distribution """
    diff_total = None
    file_arg, file_value = '--interrupts-file', '/proc/interrupts'

    def __init__(self, topology=None):
        BaseTop.default_init(self, topology)

    def post_optparse(self):
        BaseTop.default_post_optparse(self)

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
            return ''
        for line in self.repr_source():
            if line[0] == 'CPU0':
                cpu_count = len(line)
                line = self.color.colorize_cpu_list(line) + ['']
            elif self.skip_zero_line(line):  # hiding useless data such a kind of interrupt etc
                continue
            else:  # make line with irq counters as compact as we can, it can be very long!
                line = line[1: cpu_count + 1] + [line[-1]]
            output_lines.append(line)
        return output_lines, cpu_count

    @staticmethod
    def colorize_irq_per_cpu(irq_per_cpu):
        """ :returns: highlighted by warning/error irq string """
        return Color.colorize(irq_per_cpu, 40000, 80000)

    def __repr__(self):
        output_lines, cpu_count = self.make_rows()
        align_map = self.make_align_map(cpu_count)
        output_lines.insert(1, [self.colorize_irq_per_cpu(irq) for irq in self.diff_total] + ['TOTAL'])
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
