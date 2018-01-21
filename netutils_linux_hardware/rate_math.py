""" Help-functions for grade/assessor lib """
# coding=utf-8

import math
import re


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


def __str2int(value):
    result = re.sub(r'[^0-9.]+', '', value)
    try:
        return int(float(result)) if '.' in result else int(result)
    except ValueError:
        return 0


def any2int(value):
    if isinstance(value, bytes):
        value = str(value)
    if isinstance(value, str):
        value = __str2int(value)
    return int(value) if isinstance(value, int) or isinstance(value, float) else 0
