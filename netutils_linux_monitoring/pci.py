# coding=utf-8
import os
import sys

from six import print_


class PCI(object):
    """ Dealing with devices binding to NUMA nodes """
    __NODE_DIRECTORY = '/sys/devices/system/node/'
    __FAKE_DEV = {
        'eth0': 0,
        'eth1': 0,
        'eth2': 1,
        'eth3': 1,
    }
    devices = None

    def node_dev_dict(self, devices, fake=False):
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


if __name__ == '__main__':
    print_(PCI().node_dev_dict(sys.argv[1:]))
