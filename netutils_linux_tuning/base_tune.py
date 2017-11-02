# coding=utf-8

from abc import abstractmethod
from argparse import ArgumentParser

from six import iteritems

from netutils_linux_monitoring.pci import PCI


class BaseTune(object):
    """ Base class for all tuning utils """

    def __init__(self):
        self.options = self.parse_options()

    @staticmethod
    def make_parser():
        """ Make parser with options common for all tune utils """
        parser = ArgumentParser()
        parser.add_argument('-t', '--test-dir', type=str,
                            help='Use prepared test dataset in TEST_DIR directory instead of running lscpu.')
        parser.add_argument('-d', '--dry-run', help="Don't apply any settings.", action='store_true', default=False)
        return parser

    @abstractmethod
    def parse_options(self):
        """ Parse options for specific util """

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
    # pylint: disable=W0223
    topology = None
    options = None

    def __init__(self):
        BaseTune.__init__(self)
        self.pci = PCI()

    def socket_detect(self):
        """ detects socket in the same NUMA node with device """
        socket = self.pci.node_dev_dict([self.options.dev]).get(self.options.dev)
        self.options.socket = 0 if socket == -1 else socket

    @staticmethod
    def make_parser():
        """ Argument parser for CPU based tune-utils """
        parser = BaseTune.make_parser()
        parser.add_argument('-c', '--cpus', help='Explicitly define list of CPUs for binding NICs queues', type=int,
                            nargs='+')
        parser.add_argument('dev', type=str)
        parser.add_argument('socket', nargs='?', type=int)
        return parser

    def cpus_detect_real(self):
        """ :return: list of cpu ids in given socket """
        return [k for k, v in iteritems(self.topology.layout) if v == self.options.socket]
