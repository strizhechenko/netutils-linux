#!/usr/bin/env python
# coding: utf-8
# pylint: disable=C0111, C0103

import os
import re
from unittest import main, TestCase
import yaml
from autotune_network_reader import Reader


def extract(dictionary, key_sequence):
    key_sequence.reverse()
    while dictionary and key_sequence:
        dictionary = dictionary.get(key_sequence.pop())
    return dictionary


def any2int(value):
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


class Assessor(object):
    info = None
    avg = None

    def __init__(self, data):
        self.data = data
        if self.data:
            self.assess()

    def __str__(self):
        return yaml.dump(self.info, default_flow_style=False).strip()

    @staticmethod
    def grade_int(value, _min, _max, scale=10):
        value = any2int(value)
        return min(scale, max(1, int(1 + round((value - _min) * (scale - 1.) / (_max - _min)))))

    @staticmethod
    def grade_str(value, good=None, bad=None):
        if bad and value in bad:
            return 1
        if good and value in good:
            return 10
        return 2

    @staticmethod
    def grade_fact(value, mode=False):
        return int((value is None) != mode) * 10 or 1

    def grade_list(self, value, minimum, maxmimum, scale=10):
        return self.grade_int(len(value), minimum, maxmimum, scale)

    def assess_netdev(self, netdev):
        netdevinfo = extract(self.data, ['net', netdev])
        queues = sum(len(extract(netdevinfo, ['queues', x])) for x in ('rx', 'rxtx'))
        buffers = netdevinfo.get('buffers')
        return {
            'queues': self.grade_int(queues, 2, 8),
            'driver': self.grade_str(netdevinfo.get('driver').get('driver'),
                                     good=['ixgbe', 'igb', 'mlx4_en'],
                                     bad=['r8169', 'ATL1E', 'e1000', 'e1000e']),
            'buffers': {
                'cur': self.grade_int(buffers.get('cur'), 256, 4096),
                'max': self.grade_int(buffers.get('max'), 256, 4096),
            },
        }

    def assess_cpu(self):
        cpuinfo = extract(self.data, ['cpu', 'info'])
        if cpuinfo:
            return {
                'CPU MHz': self.grade_int(cpuinfo.get('CPU MHz'), 2000, 4000),
                'BogoMIPS': self.grade_int(cpuinfo.get('BogoMIPS'), 4000, 8000),
                'CPU(s)': self.grade_int(cpuinfo.get('CPU(s)'), 2, 32),
                'Core(s) per socket': self.grade_int(cpuinfo.get('Core(s) per socket'), 1, 2),
                'Socket(s)': self.grade_int(cpuinfo.get('Socket(s)'), 1, 2),
                'Thread(s) per core': self.grade_int(cpuinfo.get('Thread(s) per core'), 2, 1),
                'L3 cache': self.grade_int(cpuinfo.get('L3 cache'), 1000, 30000),
                'Vendor ID': self.grade_str(cpuinfo.get('Vendor ID'), good=['GenuineIntel']),
            }

    def assess_memory(self):
        meminfo = self.data.get('memory')
        if meminfo:
            return {
                'MemTotal': self.grade_int(meminfo.get('MemTotal'), 2 * (1024**2), 16 * (1024**2)),
                'SwapTotal': self.grade_int(meminfo.get('SwapTotal'), 512 * 1024, 4 * (1024**2)),
            }

    def assess_system(self):
        cpuinfo = extract(self.data, ['cpu', 'info'])
        if cpuinfo:
            return {
                'Hypervisor vendor': self.grade_fact(cpuinfo.get('Hypervisor vendor'), False),
                'Virtualization type': self.grade_fact(cpuinfo.get('Hypervisor vendor'), False),
            }

    def assess_disk(self, disk):
        diskinfo = extract(self.data, ['disk', disk])
        return {
            'type': self.grade_str(diskinfo.get('type'), ['SDD'], ['HDD']),
            # 50Gb - good, 1Tb - good enough
            'size': self.grade_int(diskinfo.get('size'), 50 * (1000**3), 1000**4),
        }

    def assess(self):
        self.info = {
            'net': dict((netdev, self.assess_netdev(netdev)) for netdev in self.data.get('net')),
            'cpu': self.assess_cpu(),
            'memory': self.assess_memory(),
            'system': self.assess_system(),
            'disk': dict((disk, self.assess_disk(disk)) for disk in self.data.get('disk')),
        }


class AssessorTest(TestCase):

    def test_grade_int(self):
        self.longMessage = True
        self.assertEqual(Assessor.grade_int(2000, 2000, 4000), 1)
        self.assertEqual(Assessor.grade_int(1000, 2000, 4000), 1)
        self.assertEqual(Assessor.grade_int(-1000, 2000, 4000), 1)
        self.assertEqual(Assessor.grade_int(2200, 2000, 4000), 2)
        self.assertEqual(Assessor.grade_int(3000, 2000, 4000), 6)
        self.assertEqual(Assessor.grade_int(3999, 2000, 4000), 10)
        self.assertEqual(Assessor.grade_int(4000, 2000, 4000), 10)
        self.assertEqual(Assessor.grade_int(5000, 2000, 4000), 10)
        self.assertEqual(Assessor.grade_int(5000, 2000, 4000, 15), 15)
        self.assertEqual(Assessor.grade_int(4000, 2000, 4000, 15), 15)

    def test_grade_str(self):
        bad = ["Realtek", "Dlink"]
        good = ["Intel", "Melanox"]
        expected = {
            "Melanox": 10,
            "Intel": 10,
            "Broadcom": 2,
            "Dlink": 1,
            "Realtek": 1,
        }
        for k, v in expected.iteritems():
            self.assertEqual(Assessor.grade_str(k, good, bad), v)

    def test_grade_fact(self):
        self.assertEqual(Assessor.grade_fact(None, True), 1)
        self.assertEqual(Assessor.grade_fact(None, False), 10)
        self.assertEqual(Assessor.grade_fact("Anything", True), 10)
        self.assertEqual(Assessor.grade_fact("Anything", False), 1)
        self.assertEqual(Assessor.grade_fact(15, True), 10)
        self.assertEqual(Assessor.grade_fact(15, False), 1)
        self.assertEqual(Assessor.grade_fact({'x': 'y'}, True), 10)
        self.assertEqual(Assessor.grade_fact({}, True), 10)

    def test_any2int(self):
        self.assertEqual(any2int(None), 0)
        self.assertEqual(any2int(23), 23)
        self.assertEqual(any2int(23.1), 23)
        self.assertEqual(any2int("23"), 23)
        self.assertEqual(any2int("23K"), 23)
        self.assertEqual(any2int("23 K"), 23)
        self.assertEqual(any2int(" "), 0)

    def test_grade_list(self):
        self.assertEqual(Assessor(None).grade_list([], 1, 4), 1)
        self.assertEqual(Assessor(None).grade_list([1], 1, 4), 1)
        self.assertEqual(Assessor(None).grade_list([1, 2, 3, 4], 1, 4), 10)


def __main():
    # assess data in current directory
    if os.path.isfile(os.path.join(os.getcwd(), 'lspci')):
        datadir = os.getcwd()

    # assess data in DATADIR directory
    elif os.getenv('DATADIR'):
        datadir = os.getenv('DATADIR')

    # run unit-tests
    elif os.getenv('UNITTEST'):
        main()
        return

    # default debugging routine
    else:
        datadir = 'tests/autotune_network.tests/2xE5-2640.i350_and_82599ES.l2_mixed.masterconf'
        # datadir = 'tests/autotune_network.tests/kvm.l3.masterconf'
    reader = Reader(datadir)
    data = reader.info
    # print yaml.dump(data.get('net'))
    # exit(1)
    # print reader.info.keys()
    assessments = Assessor(data)
    print assessments

if __name__ == '__main__':
    __main()
