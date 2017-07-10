# coding=utf-8

from abc import abstractmethod
from argparse import ArgumentParser


class BaseTune(object):
    """ Base class for all tuning utils """

    def __init__(self):
        self.options = self.parse_options()

    @staticmethod
    def parse_options():
        """ Parse options specific for tune """

    @abstractmethod
    def parse(self):
        """ Parse some system data required to decide how to do the best """

    @abstractmethod
    def eval(self):
        """ Decide what to do with NIC """

    @abstractmethod
    def apply(self, decision):
        """ Applying decision about NIC """


class CPUBasedTune(BaseTune):
    """ Base class for all tuning utils dealing with cpu affinity/masks """
    numa = None
    options = None

    def socket_detect(self):
        """ detects socket in the same NUMA node with device """
        socket = self.numa.node_dev_dict([self.options.dev], True).get(self.options.dev)
        self.options.socket = 0 if socket == -1 else socket

    @staticmethod
    def parse_options():
        """ Common arguments for CPU based tune-utils """
        parser = ArgumentParser()
        parser.add_argument('-t', '--test-dir', type=str,
                            help="Use prepared test dataset in TEST_DIR directory instead of running lscpu.")
        parser.add_argument('-d', '--dry-run', help="Don't apply any settings.", action='store_true', default=False)
        parser.add_argument('-c', '--cpus', help='Explicitly define list of CPUs for binding NICs queues', type=int,
                            nargs='+')
        parser.add_argument('dev', type=str)
        parser.add_argument('socket', nargs='?', type=int)
        return parser
