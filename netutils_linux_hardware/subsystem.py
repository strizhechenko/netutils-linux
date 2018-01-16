# coding=utf-8

import os
from abc import abstractmethod

from netutils_linux_hardware.folding import Folding


class Subsystem(object):
    """ Base class for CPU, Memory, etc """

    def __init__(self, data=None, folding=None, datadir=None):
        self.datadir = datadir
        self.data = data
        self.folding = folding

    @abstractmethod
    def collect(self):
        """ Collecting required data from host """
        pass

    @abstractmethod
    def parse(self):
        """ Parse that data to dict or something like this """
        pass

    @abstractmethod
    def rate(self):
        """ Rating every detail in the parsed data """
        pass

    def map(self, func, key):
        items = self.data.get(key)
        return self.folding.fold(dict((item, func(item)) for item in items), Folding.SUBSYSTEM) if items else 1

    def path(self, filename):
        assert self.datadir
        assert filename
        return os.path.join(self.datadir, filename)

    def read(self, func, filename):
        return func(self.path(filename)).result
