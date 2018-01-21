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
    if isinstance(value, str):
        value = re.sub(r'[^0-9.]+', '', value)
        try:
            value = int(float(value)) if '.' in value else int(value)
        except:
            pass
    return int(value) if isinstance(value, int) or isinstance(value, float) else 0
