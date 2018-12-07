# coding=utf-8

""" Receive Side Scaling tuning utility """

import re
import sys
from os.path import join, exists

from six import print_
from six.moves import xrange

from netutils_linux_hardware.rate_math import any2int
from netutils_linux_monitoring.colors import Color
from netutils_linux_monitoring.topology import Topology
from netutils_linux_tuning.base_tune import CPUBasedTune

MAX_QUEUE_PER_DEVICE = 16


class RSSLadder(CPUBasedTune):
    """ Distributor of queues' interrupts by multiple CPUs """

    topology = None
    color = None
    interrupts_file = None

    def __init__(self, argv=None):
        if argv:
            sys.argv = [sys.argv[0]] + argv
        CPUBasedTune.__init__(self)
        self.interrupts_file, lscpu_output = self.parse()
        if not exists(self.interrupts_file):  # unit-tests
            return
        self.parse_cpus(lscpu_output)
        self.eval()

    def parse(self):
        """ Detects sources of system data """
        interrupts_file = '/proc/interrupts'
        lscpu_output = None
        if self.options.test_dir:
            interrupts_file = join(self.options.test_dir, 'interrupts')
            lscpu_output_filename = join(self.options.test_dir, 'lscpu_output')
            lscpu_output = open(lscpu_output_filename).read()
            # Popen.stdout: python 2.7 returns <str>, 3.6 returns <bytes>
            # read() in both cases return <str>
            if isinstance(lscpu_output, bytes):
                lscpu_output = str(lscpu_output)
        return interrupts_file, lscpu_output

    def eval(self):
        """ Top of all the logic, decide what to do and then apply new settings """
        interrupts = open(self.interrupts_file).readlines()
        extract_func = self.queue_suffix_extract if 'pci' in self.options.dev else self.queue_postfix_extract
        for queue_pattern in sorted(self.queue_pattern_detect(interrupts, extract_func)):
            self.apply(self.__eval(queue_pattern, interrupts))

    def apply(self, decision):
        """
        '* 4' is in case of NIC has more queues than socket has CPUs
        :param decision: list of tuples(irq, queue_name, socket)
        """
        affinity = list(decision)
        cpus = [socket_cpu for irq, queue, socket_cpu in affinity]
        if len(set(cpus)) != len(cpus):
            warning = 'WARNING: some CPUs process multiple queues, consider reduce queue count for this network device'
            if self.options.color:
                print_(self.color.wrap(warning, Color.YELLOW))
            else:
                print_(warning)
        for irq, queue_name, socket_cpu in affinity:
            print_("  - {0}: queue {1} (irq {2}) bound to CPU{3}".format(
                self.dev_colorize(), queue_name, irq, self.cpu_colorize(socket_cpu)))
            if self.options.dry_run:
                continue
            filename = '/proc/irq/{0}/smp_affinity_list'.format(irq)
            with open(filename, 'w') as irq_file:
                irq_file.write(str(socket_cpu))

    def queue_name_regex(self, queue_pattern):
        """
        :param queue_pattern: -TxRx- or mlx5_comp
        :return: regex to much entire queue name
        """
        if 'pci' in self.options.dev:
            # mlx5_comp0@pci:0000:01:00.0
            return r'{1}[0-9]+@{0}'.format(self.options.dev, queue_pattern)
        # eth0-TxRx-[^ \n]+
        return r'{0}{1}[^ \n]+'.format(self.options.dev, queue_pattern)

    def __eval(self, queue_pattern, interrupts):
        """
        :param queue_pattern: '-TxRx-'
        :return: list of tuples(irq, queue_name, cpu)
        """
        print_('- distribute interrupts of {0} ({1}) on socket {2}'.format(
            self.options.dev, queue_pattern, self.options.socket))
        queue_regex = self.queue_name_regex(queue_pattern)
        rss_cpus = self.rss_cpus_detect()
        for _ in xrange(self.options.offset):
            rss_cpus.pop()
        for line in interrupts:
            queue_name = re.findall(queue_regex, line)
            if queue_name:
                yield any2int(line.split()[0]), queue_name[0], rss_cpus.pop()

    def parse_cpus(self, lscpu_output):
        """
        :param lscpu_output: string, output of `lscpu -p`
        """
        if self.options.cpus:  # no need to detect topology if user gave us cpu list
            return
        self.topology = Topology(lscpu_output=lscpu_output)
        self.color = Color(self.topology, self.options.color)
        if not any([self.options.socket is not None, self.options.cpus]):
            self.socket_detect()
        self.pci.devices = self.pci.node_dev_dict([self.options.dev], False)

    def queue_postfix_extract(self, line):
        """
        used for device based queue-naming
        :param line: '31312 0 0 0 blabla eth0-TxRx-0'
        :return: '-TxRx-'
        """
        queue_regex = r'{0}[^ \n]+'.format(self.options.dev)
        queue_name = re.findall(queue_regex, line)
        if queue_name:
            return re.sub(r'({0}|[0-9])'.format(self.options.dev), '', queue_name[0])

    def queue_suffix_extract(self, line):
        """
        used for pci-bus-id based queue-naming
        :param line: '33:  122736116 0 0 5465612 PCI-MSI-edge mlx5_comp3@pci:0000:01:00.0'
        :return: mlx5_comp
        """
        queue_regex = r'[^ ]*{0}'.format(self.options.dev)
        queue_name = re.findall(queue_regex, line)
        if not queue_name:
            return
        if '@' in queue_name[0]:
            queue_name = queue_name[0].split('@')  # ['mlx5_comp3', 'pci:0000:01:00.0']
        return re.sub(r'({0}|[0-9]+$)'.format(self.options.dev), '', queue_name[0])

    @staticmethod
    def queue_pattern_detect(interrupts, extract_func):
        """
        self.dev: eth0 or pci:0000:01:00.0
        :param interrupts: lines of /proc/interrupts
        :param extract_func: function to extract queue pattern from lines
        :return: set(['-TxRx-']) or set(['mlx5_comp'])
        """
        return set([line for line in [extract_func(line) for line in interrupts] if line])

    def rss_cpus_detect(self):
        """
        :return: list of cpu ids to use with current queues distribution
        """
        rss_cpus = self.options.cpus if self.options.cpus else self.cpus_detect_real()
        rss_cpus.reverse()
        return rss_cpus * MAX_QUEUE_PER_DEVICE

    def dev_colorize(self):
        """
        :return: highlighted by NUMA-node name of the device
        """
        if not self.pci or not self.options.color or not self.pci.devices:
            return self.options.dev
        dev_color = self.pci.devices.get(self.options.dev)
        color = self.color.COLORS_NODE.get(dev_color)
        return self.color.wrap(self.options.dev, color)

    def cpu_colorize(self, cpu):
        """
        :param cpu: cpu number (0)
        :return: highlighted by NUMA-node cpu number.
        """
        if not self.topology:
            return cpu
        return self.color.wrap(cpu, self.color.colorize_cpu(cpu))

    def parse_options(self):
        """
        :return: parsed arguments
        """
        parser = CPUBasedTune.make_parser()
        parser.add_argument('--no-color', help='Disable all highlights', dest='color', action='store_false',
                            default=True)
        parser.add_argument('-o', '--offset', type=int, default=0,
                            help='If you have 2 NICs with 4 queues and 1 socket with 8 cpus, you may be want '
                                 'distribution like this: eth0: [0, 1, 2, 3]; eth1: [4, 5, 6, 7]; '
                                 'so run: rss-ladder-test eth0; rss-ladder-test --offset=4 eth1')
        return parser.parse_args()


if __name__ == '__main__':
    RSSLadder()
