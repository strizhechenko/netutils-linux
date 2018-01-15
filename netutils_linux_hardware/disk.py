# coding=utf-8

from netutils_linux_hardware.grade import Grade
from netutils_linux_hardware.rater_math import extract
from netutils_linux_hardware.subsystem import Subsystem


class Disk(Subsystem):
    def rate(self):
        return self.map(self.rate_disk, 'disk')

    def rate_disk(self, disk):
        diskinfo = extract(self.data, ['disk', disk])
        return self.folding.fold({
            'type': Grade.str(diskinfo.get('type'), ['SDD'], ['HDD']),
            # 50Gb - good, 1Tb - good enough
            'size': Grade.int(diskinfo.get('size'), 50 * (1000 ** 3), 1000 ** 4),
        }, self.folding.DEVICE)
