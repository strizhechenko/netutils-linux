# coding=utf-8

from netutils_linux_hardware.grade import Grade
from netutils_linux_hardware.subsystem import Subsystem


class Memory(Subsystem):
    """ Everything about Memory: type, speed, size, swap """

    def parse(self):
        pass

    def rate(self):
        meminfo = self.data.get('memory')
        if meminfo:
            return self.folding.fold({
                'devices': self.__devices(meminfo.get('devices')),
                'size': self.__size(meminfo.get('size')),
            }, self.folding.SUBSYSTEM)

    def __devices(self, devices):
        if not devices:
            return 1
        return self.folding.fold(dict((handle, self.__device(device))
                                      for handle, device in devices.items()),
                                 self.folding.SUBSYSTEM)

    def __device(self, device):
        return self.folding.fold({
            'size': Grade.int(device.get('size', 0), 512, 8196),
            'type': Grade.known_values(device.get('type', 'RAM'), {
                'DDR1': 2,
                'DDR2': 3,
                'DDR3': 6,
                'DDR4': 10,
            }),
            'speed': Grade.int(device.get('speed', 0), 200, 4000),
        }, self.folding.DEVICE)

    def __size(self, size):
        return self.folding.fold({
            'MemTotal': Grade.int(size.get('MemTotal'), 2 * (1024 ** 2), 16 * (1024 ** 2)),
            'SwapTotal': Grade.int(size.get('SwapTotal'), 512 * 1024, 4 * (1024 ** 2)),
        }, self.folding.DEVICE) if size else 1
