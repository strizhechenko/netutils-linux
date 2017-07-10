# coding=utf-8
""" Receive Packet Steering tuning utility """
import os
from argparse import ArgumentParser

from six import print_, iteritems

from netutils_linux_monitoring.numa import Numa
from netutils_linux_tuning.base_tune import BaseTune


class AutoRPS(BaseTune):
    """ Allows to use multi-cpu packets processing for budget NICs """
    numa = None

    def __init__(self):
        BaseTune.__init__(self)
        queues = self.parse()
        self.eval()
        self.apply(queues)

    def parse(self):
        """ :return: queue list to write cpu mask """
        return ['rx-0'] if self.options.test_dir else self.detect_queues_real()

    def eval(self):
        """ Evaluates CPU mask used as decision for the apply() """
        self.numa = Numa(lscpu_output=self.lscpu())
        self.socket_detect()
        self.mask_detect()

    def apply(self, decision):
        """
        :param decision: queue list to write cpu mask
        """
        if len(decision) > 1 and not self.options.force:
            raise OSError("Refuse to use RPS on multiqueue NIC. You may use --force flag to apply RPS for all queues")
        queue_dir = "/sys/class/net/{0}/queues/".format(self.options.dev)
        for queue in decision:
            print_("Using mask '{0}' for {1}-{2}".format(self.options.cpu_mask, self.options.dev, queue))
            if self.options.dry_run:
                continue
            with open(os.path.join(queue_dir, queue, 'rps_cpus'), 'w') as queue_file:
                queue_file.write(self.options.cpu_mask)

    @staticmethod
    def parse_options():
        """
        :return: options for AutoRPS
        """
        parser = ArgumentParser()
        parser.add_argument('-t', '--test-dir', type=str,
                            help="Use prepared test dataset in TEST_DIR directory instead of running lscpu.")
        parser.add_argument('-d', '--dry-run', help="Don't write anything to smp_affinity_list.",
                            action='store_true', default=False)
        parser.add_argument('-f', '--force', help="Work even in case of multiqueue CPU", action='store_true',
                            default=False)
        parser.add_argument('-c', '--cpus', help='Explicitly define list of CPUs for binding NICs queues', type=int,
                            nargs='+')
        parser.add_argument('-m', '--cpu-mask', help='Explicitly define mask to write in rps_cpus', type=str)
        parser.add_argument('dev', type=str)
        parser.add_argument('socket', nargs='?', type=int)
        return parser.parse_args()

    @staticmethod
    def cpus2mask(cpus, cpus_count):
        """ There's no need to fill mask with zeroes, kernel does it automatically.

        :param cpus: which cpus to use in mask calculation (e.g. [4,5,6,7])
        :param cpus_count: how many cpus in this system (e.g. 8)
        :return: cpu_mask to apply
        """
        bitmap = [0] * cpus_count
        for cpu in cpus:
            bitmap[cpu] = 1
        return hex(int("".join([str(cpu) for cpu in bitmap]), 2))[2:]  # no need to write 0x

    def mask_detect(self):
        """
        Finds a way to calculate CPU mask to apply:
        1. --cpu-mask
        2. --cpus
        3. numa.layout
        """
        if self.options.cpu_mask:
            return
        if not self.options.cpus:
            self.detect_cpus()
        self.options.cpu_mask = self.cpus2mask(self.options.cpus, len(self.numa.socket_layout.keys()))

    def detect_cpus(self):
        """ detects list of cpus which belong to given socket """
        self.options.cpus = [k for k, v in iteritems(self.numa.socket_layout) if v == self.options.socket]

    def socket_detect(self):
        """ detects socket in the same NUMA node with device or just using socket given in arguments """
        if any([self.options.socket is not None, self.options.cpus, self.options.cpu_mask]):
            return
        socket = self.numa.node_dev_dict([self.options.dev], True).get(self.options.dev)
        self.options.socket = 0 if socket == -1 else socket

    def detect_queues_real(self):
        """
        :return: queue list to write cpu mask found by really reading /sys/
        """
        queue_dir = "/sys/class/net/{0}/queues/".format(self.options.dev)
        return [queue for queue in os.listdir(queue_dir) if queue.startswith('rx')]

    def lscpu(self):
        """
        :return: `lscpu -p` output if test dir given (need for NUMA-node)
        """
        if not self.options.test_dir:
            return
        lscpu_output_filename = os.path.join(self.options.test_dir, "lscpu_output")
        lscpu_output = open(lscpu_output_filename).read()
        return str(lscpu_output) if isinstance(lscpu_output, bytes) else lscpu_output
