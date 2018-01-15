""" Help-functions for grade/assessor lib """
# coding=utf-8

import re
import math


def round_(value, precision=0):
    """
    :param value: float value
    :param precision: how much digits after ',' we need
    :return: rounded float value
    """
    precision = 10 ** precision
    return float(math.floor((value * precision) + math.copysign(0.5, value))) / precision


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
        value = re.sub(r'[^0-9]', '', value)
        if value.isdigit():
            return int(value)
    elif isinstance(value, float):
        return int(value)
    return 0
