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


class CPULayout(Parser):

    @staticmethod
    def parse(text):
        output = dict((line.strip().split()) for line in text.strip().split('\n'))
        del output['CPU']
        return output


class BrctlOutput(Parser):

    @staticmethod
    def parse(text):
        netdevs_keys = [line.split()[3] for line in text.strip().split('\n')[1:]]
        netdevs = dict()
        for key in netdevs_keys:
            if key.count('.') == 1:
                dev, _ = key.split('.')
            elif key.count('.') == 0:
                dev = key
            else:
                raise NotImplementedError, 'QinQ not supported yet.'

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
