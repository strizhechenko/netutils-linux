# coding=utf-8

from collections import defaultdict

import yaml

from netutils_linux_hardware.grade import Grade
from netutils_linux_hardware.parser import Parser
from netutils_linux_hardware.rate_math import extract
from netutils_linux_hardware.subsystem import Subsystem


class Disk(Subsystem):
    def parse(self):
        return DiskInfo().parse(
            self.path('disks_types'),
            self.path('lsblk_sizes'),
            self.path('lsblk_models')
        )

    def rate(self):
        return self.map(self.rate_disk, 'disk')

    def rate_disk(self, disk):
        diskinfo = extract(self.data, ['disk', disk])
        return self.folding.fold({
            'type': Grade.str(diskinfo.get('type'), ['SDD'], ['HDD']),
            # 50Gb - good, 1Tb - good enough
            'size': Grade.int(diskinfo.get('size'), 50 * (1000 ** 3), 1000 ** 4),
        }, self.folding.DEVICE)


class DiskInfo(object):
    @staticmethod
    def invert_dict_nesting(origin):
        """
        origin = {
            'x': {'xx': 1, 'yy': 2},
            'y': {'xx': 3, 'yy': 4},
        }
        result = {
            'xx': {'x': 1, 'y': 3},
            'yy': {'x': 2, 'y': 4},
        }
        """
        result = defaultdict()
        for out_key, out_value in origin.items():
            for in_key, in_value in out_value.items():
                result.setdefault(in_key, dict())
                result[in_key][out_key] = in_value
        return dict(result)

    def parse(self, types, sizes, models):
        types_data = self.DiskTypesInfo().parse_file_safe(types)
        if not types_data:
            return
        disk_data = {
            'type': types_data,
            'size': self.DiskSizeInfo(types_data).parse_file_safe(sizes),
            'model': self.DiskModelsInfo(types_data).parse_file_safe(models),
        }
        return self.invert_dict_nesting(disk_data)

    class DiskTypesInfo(Parser):

        @staticmethod
        def parse(text):
            types = ['SSD', 'HDD']
            if not text:
                return dict()
            data = yaml.load(text.replace(':', ': ').replace('/sys/block/', '').replace('/queue/rotational', ''))
            return dict((k, types[v]) for k, v in data.items())

    class DiskSizeInfo(Parser):

        def __init__(self, types_data):
            self.types_data = set(types_data)

        def parse(self, text):
            # split grepped text into list
            data = (line.split() for line in text.strip().split('\n'))
            # remove partitions, we're interested only in disk-drives
            data = (line if len(line) == 2 else [line[0], line[2]] for line in data if
                    set(line).intersection(self.types_data))
            return dict((k, int(v)) for v, k in data)

    class DiskModelsInfo(Parser):

        def __init__(self, types_data):
            self.types_data = types_data

        def parse(self, text):
            lines = [line.split(None, 1) for line in text.strip().split('\n')]
            data = dict(line if len(line) == 2 else line + [None] for line in lines)
            if data.get('NAME'):
                del data['NAME']
            return data
