# coding=utf-8

from six import print_

from netutils_linux_hardware.collect import Collector
from netutils_linux_hardware.cpu import CPU
from netutils_linux_hardware.disk import Disk
from netutils_linux_hardware.folding import Folding
from netutils_linux_hardware.memory import Memory
from netutils_linux_hardware.net import Net
from netutils_linux_hardware.system import System
from netutils_linux_hardware.yaml_tools import dict2yaml


class Server(object):
    """ Knows about list of subsystems, folds data, etc """

    subsystems = {
        'net': Net,
        'cpu': CPU,
        'system': System,
        'memory': Memory,
        'disk': Disk,
    }

    def __init__(self, args):
        self.args = args
        self.tarball, self.directory = self.tarball_directory()

    def tarball_directory(self):
        """ Decision about and smart 'corrections' """
        suffix = '.tar.gz'
        if self.args.directory.endswith(suffix):
            return self.args.directory, self.args.directory[:-7]
        return (self.args.directory.rstrip('/') + suffix) if self.args.gzip else None, self.args.directory

    def collect(self):
        return Collector(self.directory, self.tarball, self.args.collect)

    def read(self):
        """ Parser of raw saved data info dictionary """
        info = dict()
        for key, subsystem in self.subsystems.items():
            if key != 'system' and getattr(self.args, key):
                info[key] = subsystem(datadir=self.directory).parse()
        if not self.args.cpu and self.args.system:
            info['cpu'] = CPU(datadir=self.directory).parse()
        return info

    def rate(self):
        """ Rater of parsed data """
        info = self.read()
        folding = Folding(self.args)
        rates = dict()
        for key, subsystem in self.subsystems.items():
            if getattr(self.args, key):
                rates[key] = subsystem(info, folding).rate()
        return folding.fold(rates, Folding.SERVER)

    def main(self):
        self.collect()
        if self.args.show:
            print_(dict2yaml(self.read()))
        elif self.args.rate:
            print_(dict2yaml(self.rate()))
