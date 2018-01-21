# coding=utf-8
import yaml
from six import iteritems

from netutils_linux_hardware.grade import Grade
from netutils_linux_hardware.parser import YAMLLike, Parser
from netutils_linux_hardware.subsystem import Subsystem


class Memory(Subsystem):
    """ Everything about Memory: type, speed, size, swap """

    def parse(self):
        return {
            'size': self.read(MemInfo, 'meminfo'),
            'devices': self.read(MemInfoDMI, 'dmidecode'),
        }

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


class MemInfo(YAMLLike):
    keys_required = (
        'MemTotal',
        'MemFree',
        'SwapTotal',
        'SwapFree',
    )

    def parse(self, text):
        return dict((k, int(v.replace(' kB', ''))) for k, v in iteritems(yaml.load(text)) if k in self.keys_required)


class MemInfoDMIDevice(object):
    def __init__(self, text):
        self.data = {
            'speed': 0,
            'type': 'RAM',
            'size': 0,
        }
        self.handle = None
        self.parse_text(text)

    def parse_text(self, text):
        """ Разбор описания плашки памяти от dmidecode """
        for line in map(str.strip, text.split('\n')):
            self.parse_line(line)

    def parse_line(self, line):
        for key in ('Speed', 'Type', 'Size'):
            if line.startswith(key + ':'):
                self.data[key.lower()] = line.split()[1]
                break
        if line.startswith('Handle'):
            self.handle = line.split(' ')[1].strip(',')


class MemInfoDMI(Parser):
    @staticmethod
    def parse(text):
        """ Разбор всего вывода dmidecode --type memory """
        return MemInfoDMI.__parse(text.split('\n\n')) if text else None

    @staticmethod
    def __parse(devices):
        output = dict()
        for device in devices:
            if 'Memory Device' not in device:
                continue
            mem_dev = MemInfoDMIDevice(device)
            if mem_dev.data.get('size') == 'No':
                continue
            output[mem_dev.handle] = mem_dev.data
        return output
