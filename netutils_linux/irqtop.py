from os import getenv
from top import Top
from copy import deepcopy


class IrqTop(Top):
    diff_total = None

    def __init__(self, filename='/proc/interrupts'):
        Top.__init__(self, filename)
        self.skipzero = bool(getenv('SKIPZERO', True))
        self.ignore_limit = int(getenv('IGNORE_LE', 80))

    def parse(self):
        with open(self.filename) as file_fd:
            return [[self.int(item) for item in line.strip().split()] for line in file_fd.readlines()]

    def eval(self):
        self.diff = deepcopy(self.current)
        for ln, line in enumerate(self.diff):
            for cn, column in enumerate(line):
                if isinstance(column, int):
                    self.diff[ln][cn] = column - self.previous[ln][cn]
        self.diff_total = self.eval_diff_total()

    def __repr__(self):
        repr_source = self.current if self.no_delta else self.diff
        if not self.diff_total:
            return self.header
        output_lines = [self.header, "\t".join(str(x) for x in ['Total:'] + map(str, self.diff_total))]
        for line in repr_source:
            if line[0] == 'CPU0':
                line.insert(0, ' ')
            elif self.skipzero and not self.has_diff(line) and not self.no_delta:
                continue
            output_lines.append("\t".join(map(str, line)))
        return "\n".join(output_lines)

    def eval_diff_total_column(self, column, cpucount):
        return sum(int(row[column]) for row in self.diff if len(row) > cpucount + 1)

    def eval_diff_total(self):
        cpucount = len(self.diff[0]) - 1
        return [self.eval_diff_total_column(column, cpucount) for column in xrange(1, cpucount + 2)]

    def has_diff(self, s):
        return any(x > self.ignore_limit for x in s if isinstance(x, int))


if __name__ == '__main__':
    IrqTop().run()
