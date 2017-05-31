import os


class Numa(object):
    NODE_DIRECTORY = '/sys/devices/system/node/'
    FAKE = {
        0: range(0, 4) + range(8, 12),
        1: range(4, 8) + range(12, 16),
    }
    FAKE_DEV = {
        'eth0': 0,
        'eth1': 0,
        'eth2': 1,
        'eth3': 1,
    }

    devices = None

    def __init__(self, devices=None, fake=False):
        self.nodes = self.FAKE if fake else self.node_cpu_dict()
        self.devices = self.node_dev_dict(devices, fake)

    def node_list(self):
        """ Returns list of NUMA nodes represented in current system """
        if not os.path.isdir(self.NODE_DIRECTORY):
            return []
        return [node for node in os.listdir(self.NODE_DIRECTORY) if node.startswith('node')]

    def cpulist_read(self, node):
        """ Returns list of CPUs binded to given NUMA node """
        with open(self.NODE_DIRECTORY + node + '/cpulist') as fd:
            return list(self.cpulist_parse(fd.read()))

    @staticmethod
    def cpulist_parse(cpulist):
        """ Parse cpulist notation like '1-7,15-21' or '1,2,3,4' into plain list """
        cpu_ranges = cpulist.split(',')
        if '-' not in cpulist:
            for cpu in cpu_ranges:
                yield int(cpu)
        else:
            for _min, _max in [map(int, r.split('-')) for r in cpu_ranges]:
                for cpu in range(_min, _max+1):
                    yield cpu

    def node_cpu_dict(self):
        """ return cpu layout with NUMA nodes like a {0: [0,1,2,3,], 1: [4,5,6,7]} """
        return dict((int(node.strip('node')), self.cpulist_read(node)) for node in self.node_list())

    def cpu_node(self, cpu):
        """ Determines which NUMA node given CPU belongs to """
        for node, cpus in self.nodes.iteritems():
            if cpu in cpus:
                return node
        return -1

    def node_dev_dict(self, devices, fake):
        """ Returns NIC's NUMA bindings dict like {'eth1': 0, 'eth2': 1, 'eth3': 0} """
        if not devices:
            return dict()
        return dict((dev, self.dev_node(dev, fake)) for dev in devices)

    def dev_node(self, dev, fake=False):
        """ Determines which NUMA node given network device belongs to """
        if fake:
            return self.FAKE_DEV.get(dev, -1)
        filename = '/sys/class/net/{0}/device/numa_node'.format(dev)
        if not os.path.isfile(filename):
            return -1
        with open(filename) as fd:
            return int(fd.read().strip())


if __name__ == '__main__':
    print Numa().nodes
