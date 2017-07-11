# coding=utf-8

""" Receive Side Scaling tuning utility """

import re
import sys
from os.path import join, exists

from six import print_
from six.moves import xrange

from netutils_linux_tuning.base_tune import CPUBasedTune
from netutils_linux_hardware.assessor_math import any2int
from netutils_linux_monitoring.numa import Numa
from netutils_linux_monitoring.colors import wrap, YELLOW, cpu_color, COLORS_NODE

MAX_QUEUE_PER_DEVICE = 16


class RSSLadder(CPUBasedTune):
    """ Distributor of queues' interrupts by multiple CPUs """

    numa = None
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
            interrupts_file = join(self.options.test_dir, "interrupts")
            lscpu_output_filename = join(self.options.test_dir, "lscpu_output")
            lscpu_output = open(lscpu_output_filename).read()
            # Popen.stdout: python 2.7 returns <str>, 3.6 returns <bytes>
            # read() in both cases return <str>
            if isinstance(lscpu_output, bytes):
                lscpu_output = str(lscpu_output)
        return interrupts_file, lscpu_output

    def eval(self):
        """ Top of all the logic, decide what to do and then apply new settings """
        interrupts = open(self.interrupts_file).readlines()
        for postfix in sorted(self.queue_postfixes_detect(interrupts)):
            self.apply(self.__eval(postfix, interrupts))

    def apply(self, decision):
        """
        '* 4' is in case of NIC has more queues than socket has CPUs
        :param decision: list of tuples(irq, queue_name, socket)
        """
        affinity = list(decision)
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

    def __eval(self, postfix, interrupts):
        """
        :param postfix: "-TxRx-"
        :return: list of tuples(irq, queue_name, socket)
        """
        print_("- distribute interrupts of {0} ({1}) on socket {2}".format(
            self.options.dev, postfix, self.options.socket))
        queue_regex = r'{0}{1}[^ \n]+'.format(self.options.dev, postfix)
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
        self.numa = Numa(lscpu_output=lscpu_output)
        if not any([self.options.socket is not None, self.options.cpus]):
            self.socket_detect()
        self.numa.devices = self.numa.node_dev_dict([self.options.dev], False)

    def queue_postfix_extract(self, line):
        """
        :param line: "31312 0 0 0 blabla eth0-TxRx-0"
        :return: "-TxRx-"
        """
        queue_regex = r'{0}[^ \n]+'.format(self.options.dev)
        queue_name = re.findall(queue_regex, line)
        if queue_name:
            return re.sub(r'({0}|[0-9])'.format(self.options.dev), '', queue_name[0])

    def queue_postfixes_detect(self, interrupts):
        """
        self.dev: eth0
        :return: "-TxRx-"
        """
        return set([line for line in [self.queue_postfix_extract(line) for line in interrupts] if line])

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

    def parse_options(self):
        """
        :return: parsed arguments
        """
        parser = CPUBasedTune.make_parser()
        parser.add_argument('--no-color', help='Disable all highlights', dest='color', action='store_false',
                            default=True)
        parser.add_argument('-o', '--offset', type=int, default=0,
                            help="If you have 2 NICs with 4 queues and 1 socket with 8 cpus, you may be want "
                                 "distribution like this: eth0: [0, 1, 2, 3]; eth1: [4, 5, 6, 7]; "
                                 "so run: rss-ladder-test eth0; rss-ladder-test --offset=4 eth1")
        return parser.parse_args()


if __name__ == '__main__':
    RSSLadder()
