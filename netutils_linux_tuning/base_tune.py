# coding=utf-8
from abc import abstractmethod


class BaseTune(object):
    def __init__(self):
        self.options = self.parse_options()

    @staticmethod
    @abstractmethod
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
