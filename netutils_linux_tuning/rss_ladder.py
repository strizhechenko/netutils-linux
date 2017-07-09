# coding=utf-8

""" Receive Side Scaling tuning utility """

import re
import sys
from argparse import ArgumentParser
from os.path import join, exists

from six import iteritems, print_
from six.moves import xrange

from netutils_linux_hardware.assessor_math import any2int
from netutils_linux_monitoring.numa import Numa
from netutils_linux_monitoring.colors import wrap, YELLOW, cpu_color, COLORS_NODE

MAX_QUEUE_PER_DEVICE = 16


class RSSLadder(object):
    """ Distributor of queues' interrupts by multiple CPUs """

    def __init__(self, argv=None):
        interrupts_file = '/proc/interrupts'
        if argv:
            sys.argv = [sys.argv[0]] + argv
        self.options = self.parse_options()
        lscpu_output = None
        if self.options.test_dir:
            interrupts_file = join(self.options.test_dir, "interrupts")
            lscpu_output_filename = join(self.options.test_dir, "lscpu_output")
            lscpu_output = open(lscpu_output_filename).read()
            # Popen.stdout: python 2.7 returns <str>, 3.6 returns <bytes>
            # read() in both cases return <str>
            if isinstance(lscpu_output, bytes):
                lscpu_output = str(lscpu_output)
        if not exists(interrupts_file):  # unit-tests
            return
        self.interrupts = open(interrupts_file).readlines()
        if not self.options.cpus:  # no need to detect topology if user gave us cpu list
            self.numa = Numa(lscpu_output=lscpu_output)
            self.socket_detect()
            self.numa.devices = self.numa.node_dev_dict([self.options.dev], False)
        for postfix in sorted(self.queue_postfixes_detect()):
            self.smp_affinity_list_apply(self.smp_affinity_list_make(postfix))

    def socket_detect(self):
        if any([self.options.socket is not None, self.options.cpus]):
            return
        socket = self.numa.node_dev_dict([self.options.dev], True).get(self.options.dev)
        self.options.socket = 0 if socket == -1 else socket

    @staticmethod
    def parse_options():
        """
        :return: parsed arguments
        """
        parser = ArgumentParser()
        parser.add_argument('-t', '--test-dir', type=str,
                            help="Use prepared test dataset in TEST_DIR directory instead of /proc/interrupts.")
        parser.add_argument('-d', '--dry-run', help="Don't write anything to smp_affinity_list.",
                            action='store_true', default=False)
        parser.add_argument('--no-color', help='Disable all highlights', dest='color', action='store_false',
                            default=True)
        parser.add_argument('-o', '--offset', type=int, default=0,
                            help="If you have 2 NICs with 4 queues and 1 socket with 8 cpus, you may be want "
                                 "distribution like this: eth0: [0, 1, 2, 3]; eth1: [4, 5, 6, 7]; "
                                 "so run: rss-ladder-test eth0; rss-ladder-test --offset=4 eth1")
        parser.add_argument('-c', '--cpus', help='Explicitly define list of CPUs for binding NICs queues', type=int,
                            nargs='+')
        parser.add_argument('dev', type=str)
        parser.add_argument('socket', nargs='?', type=int)
        return parser.parse_args()

    def queue_postfix_extract(self, line):
        """
        :param line: "31312 0 0 0 blabla eth0-TxRx-0"
        :return: "-TxRx-"
        """
        queue_regex = r'{0}[^ \n]+'.format(self.options.dev)
        queue_name = re.findall(queue_regex, line)
        if queue_name:
            return re.sub(r'({0}|[0-9])'.format(self.options.dev), '', queue_name[0])

    def queue_postfixes_detect(self):
        """
        self.dev: eth0
        :return: "-TxRx-"
        """
        return set([line for line in [self.queue_postfix_extract(line) for line in self.interrupts] if line])

    def smp_affinity_list_make(self, postfix):
        """
        :param postfix: "-TxRx-"
        :return: list of tuples(irq, queue_name, socket)
        """
        print_("- distribute interrupts of {0} ({1}) on socket {2}".format(
            self.options.dev, postfix, self.options.socket))
        queue_regex = r'{0}{1}[^ \n]+'.format(self.options.dev, postfix)
        if self.options.cpus:
            # 16 is in case of someone decide to bind up to 16 queues to one CPU for cache locality
            # and manually distribute workload by RPS to other CPUs.
            rss_cpus = self.options.cpus * MAX_QUEUE_PER_DEVICE
        else:
            cpus = [k for k, v in iteritems(self.numa.socket_layout) if v == self.options.socket]
            rss_cpus = cpus * MAX_QUEUE_PER_DEVICE
        rss_cpus.reverse()
        for _ in xrange(self.options.offset):
            rss_cpus.pop()
        for line in self.interrupts:
            queue_name = re.findall(queue_regex, line)
            if queue_name:
                yield any2int(line.split()[0]), queue_name[0], rss_cpus.pop()

    def dev_colorize(self):
        """
        :return: highlighted by NUMA-node name of the device
        """
        if not self.numa or not self.options.color:
            return self.options.dev
        color = COLORS_NODE.get(self.numa.devices.get(self.options.dev))
        return wrap(self.options.dev, color)

    def cpu_colorize(self, cpu):
        """
        :param cpu: cpu number (0)
        :return: highlighted by NUMA-node cpu number.
        """
        if not self.numa or not self.options.color:
            return cpu
        return wrap(cpu, cpu_color(cpu, numa=self.numa))

    def smp_affinity_list_apply(self, smp_affinity):
        """
        '* 4' is in case of NIC has more queues than socket has CPUs
        :param smp_affinity: list of tuples(irq, queue_name, socket)
        """
        affinity = list(smp_affinity)
        cpus = [socket_cpu for irq, queue, socket_cpu in affinity]
        if len(set(cpus)) != len(cpus):
            warning = "WARNING: some CPUs process multiple queues, consider reduce queue count for this network device"
            if self.options.color:
                print_(wrap(warning, YELLOW))
            else:
                print_(warning)
        for irq, queue_name, socket_cpu in affinity:
            print_("  - {0}: irq {1} {2} -> {3}".format(
                self.dev_colorize(), irq, queue_name, self.cpu_colorize(socket_cpu)))
            if self.options.dry_run:
                continue
            filename = "/proc/irq/{0}/smp_affinity_list".format(irq)
            with open(filename, 'w') as irq_file:
                irq_file.write(str(socket_cpu))


if __name__ == '__main__':
    RSSLadder()
