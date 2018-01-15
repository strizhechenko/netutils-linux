# coding=utf-8

from abc import abstractmethod

from netutils_linux_hardware.folding import Folding


class Subsystem(object):
    """ Base class for CPU, Memory, etc """

    def __init__(self, data=None, folding=None):
        self.data = data
        self.folding = folding

    @abstractmethod
    def collect(self):
        """ Collecting required data from host """
        pass

    @abstractmethod
    def parse(self):
        """ Reading collected data from datadir """
        pass

    @abstractmethod
    def rate(self):
        """ Rating every detail in that data """
        pass

    def map(self, func, key):
        items = self.data.get(key)
        return self.folding.fold(dict((item, func(item)) for item in items), Folding.SUBSYSTEM) if items else 1
