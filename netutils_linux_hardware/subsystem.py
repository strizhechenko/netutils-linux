# coding=utf-8

from abc import abstractmethod


class Subsystem(object):
    """ Base class for CPU, Memory, etc """

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
