from os import getenv
from copy import deepcopy
from top import Top
from collections import namedtuple

Stat = namedtuple('Stat', ['filename', 'shortname'])


class LinkRateTop(Top):
    stats = [
        Stat('rx_packets', 'packets'),
        Stat('rx_bytes', 'bytes'),
        Stat('rx_errors', 'errors'),
        Stat('rx_dropped', 'dropped'),
        Stat('rx_missed_errors', 'missed'),
        Stat('rx_fifo_errors', 'fifo'),
        Stat('rx_length_errors', 'length'),
        Stat('rx_over_errors', 'overrun'),
        Stat('rx_crc_errors', 'crc'),
        Stat('rx_frame_errors', 'frame'),
        Stat('tx_packets', 'packets'),
        Stat('tx_bytes', 'bytes'),
        Stat('tx_errors', 'errors')
    ]

    def __init__(self, devices=None):
        Top.__init__(self, None)
        self.devices = devices
        self.no_spaces = bool(int(getenv('NO_SPACES', 0)))
        stats_header1 = " ".join(self.__indent__(n, v) for n, v in enumerate([""] + ["RX"] * 10 + ["TX"] * 3))
        stats_header2 = " ".join(self.__indent__(n, stat.shortname) for n, stat in enumerate([Stat("", "")] + self.stats))
        self.header = "\n".join([self.header, stats_header1, stats_header2])

    def parse(self):
        return dict((dev, self.__parse_dev__(dev)) for dev in self.devices)

    def eval(self):
        self.diff = deepcopy(self.current)
        for dev, data in self.current.iteritems():
            for stat in self.stats:
                self.diff[dev][stat] = data[stat] - self.previous[dev][stat]

    def __repr__(self):
        output = [self.header]
        for dev in self.devices:
            output.append("{0:<14} {1}".format(dev, self.__repr_dev__(dev)))
        return "\n".join(output)

    def __repr_dev__(self, dev):
        repr_source = self.current if self.no_delta else self.diff
        data = [self.__indent__(n, self.__spaces__(repr_source[dev][stat]), -1) for n, stat in enumerate(self.stats)]
        return " ".join(data)

    def __parse_dev__(self, dev):
        return dict((stat, self.__parse_dev_stat__(dev, stat)) for stat in self.stats)

    @staticmethod
    def __parse_dev_stat__(dev, stat):
        with open('/sys/class/net/{0}/statistics/{1}'.format(dev, stat.filename)) as devfile:
            return int(devfile.read().strip())

    def __spaces__(self, n, sep=' '):
        if self.no_spaces:
            return n
        output = str()
        while n / 1000 > 0:
            output = str(n % 1000).zfill(3) + sep + output
            n /= 1000
        return (str(n % 1000) + sep + output).strip()

    @staticmethod
    def __indent__(n, v, maxvalue=0):
        return "{0:<14}".format(v) if n == maxvalue else "{0:>11}".format(v)

if __name__ == '__main__':
    print LinkRateTop(['eth0', 'eth1']).run()
