# coding: utf-8
from netutils_linux_hardware.assessor_math import any2int, round_


class Grade(object):
    """ Grade provides methods of grade values of any type in scale of 1..10 """
    @staticmethod
    def int(value, _min, _max, scale=10):
        value = any2int(value)
        return min(scale, max(1, int(1 + round_((value - _min) * (scale - 1.) / (_max - _min) + .001))))

    @staticmethod
    def str(value, good=None, bad=None):
        if bad and value in bad:
            return 1
        if good and value in good:
            return 10
        return 2

    @staticmethod
    def fact(value, mode=False):
        return int((value is None) != mode) * 10 or 1

