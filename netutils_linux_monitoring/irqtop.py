from random import randint
from copy import deepcopy
from optparse import Option
from netutils_linux_monitoring.base_top import BaseTop


class IrqTop(BaseTop):
    """ Utility for monitoring hardware interrupts distribution """
    diff_total = None

    def __init__(self):
        BaseTop.__init__(self)
        specific_options = [
            Option('--interrupts-file', default='/proc/interrupts',
                   help='Option for testing on MacOS purpose.')
        ]
        self.specific_options.extend(specific_options)

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

    def __repr__(self):
        if not self.diff_total:
            return self.header
        header = ['Total:'] + map(str, self.diff_total)
        output_lines = [self.header, "\t".join(str(x) for x in header)]
        for line in self.repr_source():
            if line[0] == 'CPU0':
                line.insert(0, ' ')
            elif self.skip_zero_line(line):
                continue
            output_lines.append("\t".join(map(str, line)))
        return "\n".join(output_lines)

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


if __name__ == '__main__':
    IrqTop().run()
