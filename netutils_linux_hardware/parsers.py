# coding: utf-8
# pylint: disable=C0111, C0103

import os
import yaml


class Parser(object):
    @staticmethod
    def parse(text, **kwargs):
        raise NotImplementedError

    def parse_file(self, filepath, **kwargs):
        with open(filepath) as file_for_parse:
            return self.parse(file_for_parse.read().strip(), **kwargs)

    def parse_file_safe(self, filepath, **kwargs):
        if os.path.isfile(filepath):
            return self.parse_file(filepath, **kwargs)


class YAMLLike(Parser):
    @staticmethod
    def parse(text):
        return yaml.load(text)


class ReductorMirror(Parser):
    @staticmethod
    def parse(text):
        lines = dict((line.split(' ', 1)) for line in text.strip().split('\n'))
        for netdev, conf in lines.iteritems():
            output = dict()
            output['conf'] = dict()
            output['conf']['vlan'], output['conf']['ip'] = conf.split()
            output['conf']['vlan'] = output['conf']['vlan'] == '-'
            lines[netdev] = output

        return lines


class DiskInfo(object):
    @staticmethod
    def invert_dict_nesting(d):
        """
        input = {
            'x': {'xx': 1, 'yy': 2},
            'y': {'xx': 3, 'yy': 4},
        }
        output = {
            'xx': {'x': 1, 'y': 3},
            'yy': {'x': 2, 'y': 4},
        }
        """
        d2 = dict()
        for k, v in d.iteritems():
            for k2, v2 in v.iteritems():
                if not d2.get(k2):
                    d2[k2] = dict()
                d2[k2][k] = v2
        return d2

    def parse(self, types, sizes, models):
        types_data = self.DiskTypesInfo().parse_file_safe(types)
        if not types_data:
            return
        disk_data = {
            "type": types_data,
            "size": self.DiskSizeInfo(types_data).parse_file_safe(sizes),
            "model": self.DiskModelsInfo(types_data).parse_file_safe(models),
        }
        return self.invert_dict_nesting(disk_data)

    class DiskTypesInfo(Parser):

        @staticmethod
        def parse(text):
            types = ['SSD', 'HDD']
            if not text:
                return dict()
            return dict((k, types[v]) for k, v in yaml.load(text
                                                            .replace(":", ": ")
                                                            .replace("/sys/block/", "")
                                                            .replace("/queue/rotational", ""))
                        .iteritems())

    class DiskSizeInfo(Parser):

        def __init__(self, types_data):
            self.types_data = set(types_data)

        def parse(self, text):
            data = (line.split() for line in text.strip().split('\n'))
            data = (line for line in data if set(line).intersection(self.types_data))
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


class MemInfo(YAMLLike):
    keys_required = (
        'MemTotal',
        'MemFree',
        'SwapTotal',
        'SwapFree',
    )

    def parse(self, text):
        return dict((k, int(v.replace(' kB', ''))) for k, v in yaml.load(text).iteritems() if k in self.keys_required)


class CPULayout(Parser):
    @staticmethod
    def parse(text):
        output = dict((line.strip().split())
                      for line in text.strip().split('\n'))
        del output['CPU']
        return output


class BrctlOutput(Parser):
    @staticmethod
    def parse(text):
        netdevs = dict()
        netdevs_keys = [line.split()[3]
                        for line in text.strip().split('\n')[1:]
                        if len(line.split()) > 3]
        for key in netdevs_keys:
            if key.count('.') == 1:
                dev, _ = key.split('.')
            elif key.count('.') == 0:
                dev = key
            else:
                print 'QinQ not supported yet. Device: {0}'.format(key)
                raise NotImplementedError

            netdevs[dev] = dict()
            netdevs[dev]['conf'] = {
                'vlan': key.count('.') == 1,
                'ip': '',
            }
        return netdevs


class EthtoolBuffers(Parser):
    @staticmethod
    def parse(text):
        buffers = [int(line.split()[1])
                   for line in text.strip().split('\n')
                   if line.startswith('RX:')]
        if buffers and len(buffers) == 2:
            return {
                'max': buffers[0],
                'cur': buffers[1],
            }
