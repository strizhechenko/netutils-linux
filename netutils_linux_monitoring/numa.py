""" CPU/Memory specific things: NUMA, Sockets """

# coding: utf-8

import os
from subprocess import Popen, PIPE

from six import print_

from netutils_linux_hardware.assessor_math import any2int


class Numa(object):
    """ Class handling NUMA and sockets layout and membership of net-devices """
    __NODE_DIRECTORY = '/sys/devices/system/node/'
    __FAKE_LAYOUT = {
        0: 0, 1: 0, 2: 0, 3: 0,
        4: 1, 5: 1, 6: 1, 7: 1,
        8: 0, 9: 0, 10: 0, 11: 0,
        12: 1, 13: 1, 14: 1, 15: 1,
    }
    __FAKE_DEV = {
        'eth0': 0,
        'eth1': 0,
        'eth2': 1,
        'eth3': 1,
    }
    devices = None
    layout_kind = None
    numa_layout = None
    socket_layout = None

    def __init__(self, fake=False, lscpu_output=None):
        if fake:
            self.numa_layout = self.socket_layout = self.__FAKE_LAYOUT
        else:
            self.detect_layouts(lscpu_output=lscpu_output)
        if len(set(self.numa_layout.values())) >= 2:
            self.layout = self.numa_layout
            self.layout_kind = 'NUMA'
        else:
            self.layout = self.socket_layout
            self.layout_kind = 'SOCKET'

    def node_dev_dict(self, devices, fake):
        """
        :param devices: list of devices
        :param fake: options.random
        :return: NIC's NUMA bindings dict like {'eth1': 0, 'eth2': 1, 'eth3': 0} """
        if not devices:
            return dict()
        return dict((dev, self.dev_node(dev, fake)) for dev in devices)

    def dev_node(self, dev, fake=False):
        """ Determines which NUMA node given network device belongs to """
        if fake:
            return self.__FAKE_DEV.get(dev, -1)
        filename = '/sys/class/net/{0}/device/numa_node'.format(dev)
        if not os.path.isfile(filename):
            return -1
        with open(filename) as dev_file:
            return int(dev_file.read().strip())

    def detect_layouts_fallback(self):
        """
        In case of running in container where lscpu didn't work
        """
        process = Popen(['nproc'], stdout=PIPE, stderr=PIPE)
        stdout, _ = process.communicate()
        if process.returncode != 0:
            return None
        cpu_count = int(stdout.strip())
        self.socket_layout = self.numa_layout = dict(enumerate([0] * cpu_count))

    @staticmethod
    def __detect_layout_lscpu():
        process = Popen(['lscpu', '-p'], stdout=PIPE, stderr=PIPE)
        stdout, _ = process.communicate()
        return stdout, process.returncode

    def detect_layout_lscpu(self, lscpu_output=None):
        """
        :param lscpu_output: <str> with output of `lscpu -p` or None
        :return: <str> output of `lscpu -p` or None
        """
        if lscpu_output:
            return lscpu_output
        stdout, return_code = self.__detect_layout_lscpu()
        if return_code != 0:
            return self.detect_layouts_fallback()
        if isinstance(stdout, bytes):
            stdout = str(stdout)
        return stdout

    def detect_layouts(self, lscpu_output=None):
        """ Determine NUMA and sockets layout """
        stdout = self.detect_layout_lscpu(lscpu_output)
        rows = [row for row in stdout.strip().split('\n') if not row.startswith('#')]
        layouts = [[any2int(value) for value in row.split(',')][2:4] for row in rows]
        numa_layout, socket_layout = zip(*layouts)
        self.numa_layout = dict(enumerate(numa_layout))
        self.socket_layout = dict(enumerate(socket_layout))


if __name__ == '__main__':
    NUMA = Numa()
    print_('SOCKET', NUMA.socket_layout)
    print_('NUMA', NUMA.numa_layout)
