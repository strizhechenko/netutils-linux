# coding=utf-8
""" Transmit Packet Steering tuning utility """

from netutils_linux_tuning.autorps import AutoRPS


class AutoXPS(AutoRPS):
    """ Allows to use multi-cpu packets processing for budget NICs """
    numa = None
    target = 'xps_cpus'
    queue_prefix = 'tx'

    def __init__(self):
        AutoRPS.__init__(self)
