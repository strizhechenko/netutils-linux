# coding: utf-8
import argparse
from abc import abstractmethod
from os import system
from random import randint
from time import sleep

from six import print_

from netutils_linux_monitoring.colors import Color
from netutils_linux_monitoring.topology import Topology


class BaseTop(object):
    """ Base class for all these top-like utils. """
    current = None
    previous = None
    diff = None
    header = Color.wrap('Press CTRL-C to exit...\n', Color.GREY)
    options = None
    file_arg = None
    file_value = None
    topology = None
    color = None

    @staticmethod
    def make_base_parser(parser=None):
        """ That should be explicitly called in __main__ part of any top-like utils """
        if not parser:
            parser = argparse.ArgumentParser()
        parser.add_argument('-i', '--interval', default=1, type=int,
                            help='Interval between screen renew in seconds.')
        parser.add_argument('-n', '--iterations', dest='iterations', default=60, type=int,
                            help='Count of screen\'s renews, -1 - infinite loop.')
        parser.add_argument('--no-delta-mode', action='store_false', dest='delta_mode',
                            default=True, help="Shows metrics' values instead of growth.")
        parser.add_argument('--no-delta-small-hide', action='store_false',
                            dest='delta_small_hide', default=True,
                            help='Prevent lines with only small changes or without'
                                 'changes at all from hiding.')
        parser.add_argument('-l', '--delta-small-hide-limit', default=80, type=int,
                            help='Hides lines with only changes less than this limit')
        parser.add_argument('--no-color', dest='color', default=True, action='store_false',
                            help="Don't highlight NUMA nodes or sockets")
        parser.add_argument('--spaces', default=False, action='store_true',
                            help="Add spaces in numbers' representation, e.g. '1234567' "
                                 "will be '1 234 567'")
        parser.add_argument('--random', default=False, action='store_true',
                            help='Shows random diff data instead of real evaluation. '
                                 'Helpful for testing on static files')
        parser.add_argument('--no-clear', default=True, dest='clear', action='store_false',
                            help="Don't clear screen after each iteration. "
                                 "May be useful in scripts/logging to file.")
        parser.add_argument('--lscpu-output', help='Specify file with lscpu -p output')
        return parser

    def make_parser(self, parser=None):
        if type(self) == BaseTop:
            raise TypeError('make_parser should not be called directly by BaseTop')
        if not parser:
            parser = BaseTop.make_base_parser()
        parser.add_argument(self.file_arg, default=self.file_value, help='Option for testing on MacOS purpose.')
        return parser

    def tick(self):
        """ Gathers new data + evaluate diff between current & previous data """
        self.previous = self.current
        self.current = self.parse()
        if all((self.previous, self.current)):
            self.eval()

    def list_diff(self, current, previous):
        """ It's strange that there is no [3,4,3] - [1,2,1] -> [2,2,2] in standard library """
        if self.options.random:
            return [randint(0, 10000) for _ in current]
        return [data - previous[n] for n, data in enumerate(current)]

    def run(self):
        """ Default main()-like function for specific top-like utils except meta-utils. """
        infinite = -1
        if self.options.iterations != infinite:
            self.options.iterations += 1
        try:
            while self.options.iterations > 0 or self.options.iterations == infinite:
                if self.options.iterations != infinite:
                    self.options.iterations -= 1
                sleep(self.options.interval)
                self.tick()
                if self.options.clear:
                    system('clear')
                if self.diff:
                    print_(self)
        except KeyboardInterrupt:
            print_()
            exit(0)

    def repr_source(self):
        return self.diff if self.options.delta_mode else self.current

    @staticmethod
    def int(item):
        return int(item) if item.isdigit() else item

    def spaces(self, number, sep=' '):
        """ 1234567 -> 1 234 567 """
        if not self.options.spaces:
            return number
        output = str()
        while number / 1000 > 0:
            output = str(number % 1000).zfill(3) + sep + output
            number /= 1000
        return (str(number % 1000) + sep + output).strip()

    def __repr_table__(self, table):
        if self.options.clear:
            return BaseTop.header + str(table)
        return str(table)

    def default_init(self, topology=None):
        BaseTop.__init__(self)
        self.topology = topology
        self.color = Color(self.topology)

    def default_post_optparse(self):
        if not self.topology:
            self.topology = Topology(fake=self.options.random)
            self.color = Color(self.topology, self.options.color)

    @abstractmethod
    def parse(self):
        """ Should read some file(s) into python structure (dict/list) """

    @abstractmethod
    def eval(self):
        """ Should evaluate self.diff using self.previous / self.current """

    @abstractmethod
    def __repr__(self):
        """ Should return string, representing self.diff """

    def main(self):
        """ Default entry point for most of top-like utils """
        self.options = self.make_parser().parse_args()
        if hasattr(self, 'post_optparse'):
            self.post_optparse()
        self.run()
