# coding=utf-8

import argparse

from six import print_

from netutils_linux_hardware.assessor import Assessor, FOLDING_NO, FOLDING_DEVICE, FOLDING_SUBSYSTEM, FOLDING_SERVER
from netutils_linux_hardware.collect import ServerInfoCollect
from netutils_linux_hardware.reader import Reader


class ServerInfo(object):
    """ Single entry point for --collect, --rate, --show """
    args = None
    commands = ['--collect', '--rate', '--show', '--help']

    def __init__(self):
        self.__parse_args()
        self.__check_args()
        self.main()

    def __parse_args(self):
        default_directory = '/tmp/netutils_server_info/'
        parser = argparse.ArgumentParser()
        parser.add_argument('--directory', type=str, help="Specify a data directory or a tarball",
                            default=default_directory)
        parser.add_argument('--collect', action='store_true', help='Collect the data about the server', default=False)
        parser.add_argument('--gzip', action='store_true', help="Compress the data", default=False)
        parser.add_argument('--show', action='store_true', help='Shows data about the server in YAML', default=False)
        parser.add_argument('--rate', action='store_true', help='Rates data about the server', default=False)
        parser.add_argument('-f', '--folding', action='count', help='-f - device, -ff - subsystem, -fff - server',
                            default=FOLDING_NO)
        parser.add_argument('--device', action='store_const', const=FOLDING_DEVICE, dest='folding',
                            help='Folds rates details to entire devices')
        parser.add_argument('--subsystem', action='store_const', const=FOLDING_SUBSYSTEM, dest='folding',
                            help='Folds rates details to entire subsystems')
        parser.add_argument('--server', action='store_const', const=FOLDING_SERVER, dest='folding',
                            help='Folds rates details to entire server')
        self.args = parser.parse_args()

    def __check_args(self):
        """ Maybe they should be positional arguments, not options. But subparsers/groups are stupid """
        assert any([self.args.collect, self.args.rate, self.args.show]), "Specify command: {0}".format(self.commands)

    def tarball_directory(self):
        """ Decision about and smart 'corrections' """
        suffix = '.tar.gz'
        if self.args.directory.endswith(suffix):
            return self.args.directory, self.args.directory[:-7]
        return (self.args.directory.rstrip('/') + suffix) if self.args.gzip else None, self.args.directory

    def main(self):
        """ Main logic """
        tarball, directory = self.tarball_directory()
        ServerInfoCollect(directory, tarball, self.args.collect)
        if self.args.rate or self.args.show:
            reader = Reader(directory)
            print_(Assessor(reader.info, self.args) if self.args.rate else reader)
