""" CPU/Memory specific things: NUMA, Sockets """

# coding: utf-8

import os
from subprocess import Popen, PIPE


class Numa(object):
    """ Class handling NUMA and sockets layout and membership of net-devices """
    __NODE_DIRECTORY = '/sys/devices/system/node/'
    __FAKE_LAYOUT = {
        0:  0,  1:  0,  2:  0,  3:  0,
        4:  1,  5:  1,  6:  1,  7:  1,
        8:  0,  9:  0,  10: 0,  11: 0,
        12: 1,  13: 1,  14: 1,  15: 1,
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

    def __init__(self, devices=None, fake=False):
        if fake:
            self.numa_layout = self.socket_layout = self.__FAKE_LAYOUT
        else:
            self.detect_layouts()
        if len(set(self.numa_layout.values())) >= 2:
            self.layout = self.numa_layout
            self.layout_kind = 'NUMA'
        else:
            self.layout = self.socket_layout
            self.layout_kind = 'SOCKET'
        self.devices = self.node_dev_dict(devices, fake)

    def node_dev_dict(self, devices, fake):
        """ Returns NIC's NUMA bindings dict like {'eth1': 0, 'eth2': 1, 'eth3': 0} """
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
        with open(filename) as fd:
            return int(fd.read().strip())

    def detect_layouts(self):
        """ Determine NUMA and sockets layout """
        process = Popen(['lscpu', '-e'], stdout=PIPE, stderr=PIPE)
        stdout, _ = process.communicate()
        if process.returncode != 0:
            return None
        rows = stdout.strip().split('\n')
        layouts = [map(int, row.split()[1:3]) for row in rows if 'NODE' not in row]
        numa_layout, socket_layout = zip(*layouts)
        self.numa_layout = dict(enumerate(numa_layout))
        self.socket_layout = dict(enumerate(socket_layout))


if __name__ == '__main__':
    numa = Numa()
    print 'SOCKET', numa.socket_layout
    print 'NUMA', numa.numa_layout
