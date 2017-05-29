from random import randint
from copy import deepcopy
from optparse import Option
from base_top import BaseTop


class IrqTop(BaseTop):
    diff_total = None

    def __init__(self):
        BaseTop.__init__(self)
        specific_options = [
            Option('--interrupts-file', default='/proc/interrupts',
                   help='Option for testing on MacOS purpose.')
        ]
        self.specific_options.extend(specific_options)

    def parse(self):
        with open(self.options.interrupts_file) as file_fd:
            return [[self.int(item) for item in line.strip().split()] for line in file_fd.readlines()]

    def eval(self):
        self.diff = deepcopy(self.current)
        for ln, line in enumerate(self.diff):
            for cn, column in enumerate(line):
                if isinstance(column, int):
                    if self.options.random:
                        self.diff[ln][cn] = randint(0, 10000)
                    else:
                        self.diff[ln][cn] = column - self.previous[ln][cn]
        self.diff_total = self.eval_diff_total()

    def skip_zero_line(self, line):
        return self.options.delta_small_hide and not self.has_diff(line) and self.options.delta_mode

    def __repr__(self):
        repr_source = self.diff if self.options.delta_mode else self.current
        if not self.diff_total:
            return self.header
        output_lines = [self.header, "\t".join(str(x) for x in ['Total:'] + map(str, self.diff_total))]
        for line in repr_source:
            if line[0] == 'CPU0':
                line.insert(0, ' ')
            elif self.skip_zero_line(line):
                continue
            output_lines.append("\t".join(map(str, line)))
        return "\n".join(output_lines)

    def eval_diff_total_column(self, column, cpucount):
        return sum(int(row[column]) for row in self.diff if len(row) > cpucount + 1)

    def eval_diff_total(self):
        cpucount = len(self.diff[0]) - 1
        return [self.eval_diff_total_column(column, cpucount) for column in xrange(1, cpucount + 2)]

    def has_diff(self, s):
        return any(x > self.options.delta_small_hide_limit for x in s if isinstance(x, int))


if __name__ == '__main__':
    IrqTop().run()
