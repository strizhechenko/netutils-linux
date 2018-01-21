# coding=utf-8

import argparse

from six import print_

from netutils_linux_hardware.collect import Collector
from netutils_linux_hardware.folding import Folding
from netutils_linux_hardware.server import Server


class ServerInfo(object):
    """ Single entry point for --collect, --rate, --show """
    args = None
    commands = ['--collect', '--rate', '--show', '--help']
    subsystems = ('cpu', 'memory', 'net', 'disk', 'system')

    def __init__(self):
        self.parser = argparse.ArgumentParser()
        self.__parse_args()
        self.__check_args()
        self.main()

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
        self.parser.add_argument('-f', '--folding', action='count', help='-f - device, -ff - subsystem, -fff - server',
                                 default=Folding.NO)
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
        if not any(getattr(self.args, subsystem) for subsystem in self.subsystems):
            for subsystem in self.subsystems:
                setattr(self.args, subsystem, True)

    def main(self):
        """ Main logic """
        Server(self.args).main()
