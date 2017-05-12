class SoftnetStat(object):
    def __init__(self, row, cpu):
        row = [int('0x' + x, 16) for x in row.strip().split()]
        self.total, self.dropped, self.time_squeeze = row[0:3]
        self.cpu_collision = row[6]
        self.received_rps = row[7]
        self.cpu = cpu

    def __repr__(self):
        return "CPU: {0} total: {1:11} dropped: {2} time_squeeze: {3:4} cpu_collision: {4} received_rps: {5}" \
            .format(self.cpu, self.total, self.dropped, self.time_squeeze, self.cpu_collision, self.received_rps)

    def __sub__(self, other):
        return "CPU: {0:2} total: {1:8} dropped: {2} time_squeeze: {3} cpu_collision: {4} received_rps: {5}" \
            .format(self.cpu,
                    self.total - other.total,
                    self.dropped - other.dropped,
                    self.time_squeeze - other.time_squeeze,
                    self.cpu_collision - other.cpu_collision,
                    self.received_rps - other.received_rps)

