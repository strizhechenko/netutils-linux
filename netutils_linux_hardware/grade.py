# coding: utf-8
from netutils_linux_hardware.rate_math import any2int, round_


class Grade(object):
    """ Grade provides methods of grade values of any type in scale of 1..10 """

    @staticmethod
    def int(value, _min, _max, scale=10):
        """ Well, it's tricky function writen by all the twitter """
        value = any2int(value)
        return min(scale, max(1, int(1 + round_((value - _min) * (scale - 1.) / (_max - _min) + .001))))

    @staticmethod
    def str(value, good=None, bad=None):
        return 1 if bad and value in bad else 10 if good and value in good else 2

    @staticmethod
    def fact(value, mode=False):
        return 10 if (value is None) != mode else 1

    @staticmethod
    def known_values(value, _dict):
        return _dict.get(value, 1)
