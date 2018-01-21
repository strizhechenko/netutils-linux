# coding=utf-8

import argparse
import os
import shutil

from six import print_

from netutils_linux_hardware.cpu import CPU
from netutils_linux_hardware.disk import Disk
from netutils_linux_hardware.folding import Folding
from netutils_linux_hardware.memory import Memory
from netutils_linux_hardware.net import Net
from netutils_linux_hardware.system import System
from netutils_linux_hardware.yaml_tools import dict2yaml


class Server(object):
    """ Single entry point for --collect, --rate, --show """

    args = None
    commands = ['--collect', '--rate', '--show', '--help']
    subsystems = {
        'net': Net,
        'cpu': CPU,
        'system': System,
        'memory': Memory,
        'disk': Disk,
    }

    def __init__(self):
        self.parser = argparse.ArgumentParser()
        self.__parse_args()
        self.__check_args()
        self.tarball, self.directory = self.tarball_directory()

    def tarball_directory(self):
        """ Decision about and smart 'corrections' """
        suffix = '.tar.gz'
        if self.args.directory.endswith(suffix):
            return self.args.directory, self.args.directory[:-7]
        return (self.args.directory.rstrip('/') + suffix) if self.args.gzip else None, self.args.directory

    def collect(self):
        """ Save raw data to given directory """
        already_exists = os.path.exists(self.directory)
        if already_exists and not self.args.collect:
            return
        if already_exists:
            shutil.rmtree(self.directory)
        os.makedirs(self.directory)
        os.system('server-info-collect {0}'.format(self.directory))
        self.archive()

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

    def archive(self):
        """ Create an archive of saved data if you need to fetch it from server """
        if not self.tarball:
            return
        os.chdir(os.path.join(self.directory, '..'))
        os.system('tar cfz {0} {1} 2>/dev/null'.format(self.tarball, self.directory))

    def __parse_args(self):
        default_directory = '/tmp/netutils_server_info/'
        self.parser.add_argument('--directory', type=str, help="Specify a data directory or a tarball",
                                 default=default_directory)
        self.parser.add_argument('--collect', action='store_true', help='Collect the data about the server',
                                 default=False)
        self.parser.add_argument('--gzip', action='store_true', help="Compress the data", default=False)
        self.parser.add_argument('--show', action='store_true', help='Shows data about the server in YAML',
                                 default=False)
        self.parser.add_argument('--rate', action='store_true', help='Rates data about the server', default=False)
        self.parser.add_argument('--device', action='store_const', const=Folding.DEVICE, dest='folding',
                                 help='Folds rates details to entire devices')
        self.parser.add_argument('--subsystem', action='store_const', const=Folding.SUBSYSTEM, dest='folding',
                                 help='Folds rates details to entire subsystems')
        self.parser.add_argument('--server', action='store_const', const=Folding.SERVER, dest='folding',
                                 help='Folds rates details to entire server')
        self.parser.add_argument('--cpu', action='store_true', help='Show information about CPU', default=False)
        self.parser.add_argument('--memory', action='store_true', help='Show information about RAM', default=False)
        self.parser.add_argument('--net', action='store_true', help='Show information about network devices',
                                 default=False)
        self.parser.add_argument('--disk', action='store_true', help='Show information about disks', default=False)
        self.parser.add_argument('--system', action='store_true',
                                 help='Show information about system overall (rate only)', default=False)
        self.args = self.parser.parse_args()

    def __check_args(self):
        """ Maybe they should be positional arguments, not options. But subparsers/groups are stupid """
        if not any([self.args.collect, self.args.rate, self.args.show]):
            print('Error: please, specify --rate, --show or --collect command')
            self.parser.print_help()
            exit(1)
        if self.args.folding is None:
            self.args.folding = Folding.NO
        if not any(getattr(self.args, subsystem) for subsystem in self.subsystems):
            for subsystem in self.subsystems:
                setattr(self.args, subsystem, True)

    def main(self):
        self.collect()
        if self.args.show:
            print_(dict2yaml(self.read()))
        elif self.args.rate:
            print_(dict2yaml(self.rate()))
