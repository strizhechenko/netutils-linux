# coding: utf-8
# pylint: disable=C0111, C0103

from six import print_

from netutils_linux_hardware.parser import Parser


class NICQueues(object):

    def __init__(self):
        self.queues = {
            'own': [],
            'rx': [],
            'tx': [],
            'rxtx': [],
            'shared': [],
            'unknown': [],
        }

    @staticmethod
    def netdev_queue_relationship(queue, dev):
        if dev not in queue:
            return
        if queue == dev:
            return 'own'
        if queue.startswith(dev + '-'):
            kind = queue.split('-')[1]
            if kind in ('tx', 'rx', 'rxtx'):
                return kind
            if kind.isdigit() or kind == 'TxRx':
                return 'rxtx'
            print_(queue)
        if queue.count(',') > 0 and dev in queue:
            return 'shared'
        return 'unknown'

    def parse(self, all_queues, dev):
        # maybe some nic's have no own separate queue, just rx/tx/rxtx
        for queue in all_queues:
            kind = self.netdev_queue_relationship(queue, dev)
            if kind:
                self.queues[kind].append(queue)
        return self.queues


class IRQQueueCounter(Parser):

    @staticmethod
    def all_netdev_queues(text, netdevs):
        for line in text.strip().split('\n'):
            for netdev in netdevs:
                if netdev in line:
                    yield line.strip()
                    continue

    def irq2queues(self, text, cpu_count, netdevs):
        netdev_queues = self.all_netdev_queues(text, netdevs)
        return [' '.join(line.split()[cpu_count + 2:]) for line in netdev_queues]

    @staticmethod
    def irq2cpucount(text):
        """ IDK maybe /proc/interrupts cpu count differ from nproc """
        return len(text.split('\n')[0].split())

    def parse(self, text, **kwargs):
        netdevs = kwargs['netdevs']
        cpu_count = self.irq2cpucount(text)
        queues_names = self.irq2queues(text, cpu_count, netdevs)
        for netdev in netdevs:
            netdevs[netdev]['queues'] = NICQueues().parse(queues_names, netdev)
