# coding=utf-8

import os
import argparse

from six import print_

from netutils_linux_hardware.collect import ServerInfoCollect
from netutils_linux_hardware.assessor import Assessor, FOLDING_NO, FOLDING_DEVICE, FOLDING_SUBSYSTEM, FOLDING_SERVER
from netutils_linux_hardware.reader import Reader


# set -euo pipefail
#
# if [ "$1" != 'show' ] && [ "$1" != 'rate' ]; then
# 	echo "Usage $0 [show|rate]"
# 	exit 1
# fi
# server-info-collect server
# cd /root/
# tar xfz server.tar.gz
# cd /root/server/
# server-info-"$1"

class ServerInfo(object):
    args = None
    commands = ['--collect', '--rate', '--show', '--help']

    def __init__(self):
        self.parse_args()
        self.check_args()
        self.main()

    def parse_args(self):
        """ Разбор аргументов для выбора следующей утилиты """
        parser = argparse.ArgumentParser()
        parser.add_argument('--input', type=str, help="Specify a data directory or a tarball")
        parser.add_argument('--collect', action='store_true', help='Collect the data about the server', default=False)
        parser.add_argument('--output', type=str, help="Store the data in directory")
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
        # print(self.args)

    def check_args(self):
        """ Проверка аргументов """
        assert any([self.args.collect, self.args.rate, self.args.show]), "Specify command: {0}".format(self.commands)
        if self.args.collect:
            assert self.args.output, 'Specify output directory'
        if not self.args.input:
            cwd = os.getcwd()
            if os.path.isfile(os.path.join(cwd, 'lspci')):
                self.args.input = cwd
            elif os.getenv('DATADIR'):
                self.args.input = os.getenv('DATADIR')
        assert self.args.input, 'Specify --input/DATADIR=<path> or cd into data directory'

    def main(self):
        """ Вывод необходимых данных и их сбор при необходимости """
        if not self.args.input or self.args.collect:
            ServerInfoCollect()
        if not self.args.rate and not self.args.show:
            return
        reader = Reader(self.args.input)
        print_(Assessor(reader.info) if self.args.rate else reader)
