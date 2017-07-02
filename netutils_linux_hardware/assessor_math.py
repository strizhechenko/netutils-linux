""" Help-functions for grade/assessor lib """
# coding=utf-8

import re
import math


def round_(x, d=0):
    p = 10 ** d
    return float(math.floor((x * p) + math.copysign(0.5, x))) / p


def extract(dictionary, key_sequence):
    key_sequence.reverse()
    while dictionary and key_sequence:
        dictionary = dictionary.get(key_sequence.pop())
    return dictionary


def any2int(value):
    if isinstance(value, bytes):
        value = str(value)
    if isinstance(value, int):
        return value
    elif value is None:
        return 0
    elif isinstance(value, str):
        v = re.sub(r'[^0-9]', '', value)
        if v.isdigit():
            return int(v)
    elif isinstance(value, float):
        return int(value)
    return 0
