# coding=utf-8

from six import print_

from netutils_linux_hardware.collect import Collector
from netutils_linux_hardware.rater import Rater
from netutils_linux_hardware.reader import Reader


class Server(object):
    """ Knows about list of subsystems, folds data, etc """

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
        return Reader(self.directory, self.args)

    def rate(self):
        reader = self.read()
        return Rater(reader.info, self.args)

    def main(self):
        self.collect()
        if self.args.show:
            print_(self.read())
        elif self.args.rate:
            print_(self.rate())
