# coding: utf-8
# pylint: disable=C0111, C0103

import os

import yaml
from six import print_, iteritems


class Parser(object):
    def __init__(self, filepath=None):
        self.result = self.parse_file_safe(filepath) if filepath else None

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
        for netdev, conf in iteritems(lines):
            output = dict()
            output['conf'] = dict()
            output['conf']['vlan'], output['conf']['ip'] = conf.split()
            output['conf']['vlan'] = output['conf']['vlan'] != '-'
            if output['conf']['ip'] == '-':
                output['conf']['ip'] = ''
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
        for k, v in iteritems(d):
            for k2, v2 in iteritems(v):
                if not d2.get(k2):
                    d2[k2] = dict()
                d2[k2][k] = v2
        return d2

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
            return dict((k, types[v]) for k, v in iteritems(data))

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
            if 'Memory Device' in device:
                mem_dev = MemInfoDMIDevice(device)
                if mem_dev.data.get('size') == 'No':
                    continue
                output[mem_dev.handle] = mem_dev.data
        return output


class CPULayout(Parser):
    @staticmethod
    def parse(text):
        output = dict((line.strip().split())
                      for line in text.strip().split('\n'))
        if output.get('CPU'):
            del output['CPU']
        return output


class NetdevParser(Parser):
    @staticmethod
    def parse(netdev_keys):
        """
        :param netdev_keys: list of device names
        :return: dict[device_name] = {'vlan': bool; 'ip': ''}
        """
        netdevs = dict()
        for key in netdev_keys:
            if key.count('.') == 1:
                dev, _ = key.split('.')
            elif key.count('.') == 0:
                dev = key
            else:
                print_('QinQ not supported yet. Device: {0}'.format(key))
                raise NotImplementedError
            netdevs[dev] = dict()
            netdevs[dev]['conf'] = {
                'vlan': key.count('.') == 1,
                'ip': '',
            }
        return netdevs


class BridgeOutput(NetdevParser):
    @staticmethod
    def parse(text):
        """ # 0 - id, 1 - dev, 2 - _, 3 - state, 4 - _, 5 - details, 6 - _, 7 - mtu, 8 - _, 9 - master
        :param text: # 3: eth1 state DOWN : <NO-CARRIER,BROADCAST,MULTICAST,UP> mtu 1500 master br1 state disabled
        :return: analyzed netdevs
        """
        __dev__ = 1
        netdevs_keys = [line.split()[__dev__] for line in text.strip().split('\n')]
        return NetdevParser.parse(netdevs_keys)


class EthtoolFiles(NetdevParser):
    def parse_file(self, filepath, **kwargs):
        return self.parse(os.listdir(filepath))


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
