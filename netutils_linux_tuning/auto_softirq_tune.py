# coding=utf-8
""" Transmit Packet Steering tuning utility """

import os

from six import print_

from netutils_linux_monitoring.topology import Topology
from netutils_linux_tuning.base_tune import CPUBasedTune


class AutoSoftirqTune(CPUBasedTune):
    """ Allows to use multi-cpu packets processing for budget NICs """
    topology = None
    target = None
    queue_prefix = None

    def __init__(self):
        CPUBasedTune.__init__(self)
        queues = self.parse()
        self.eval()
        self.apply(queues)

    def parse(self):
        """ :return: queue list to write cpu mask """
        return ['{0}-0'.format(self.queue_prefix)] if self.options.test_dir else self.detect_queues_real()

    def eval(self):
        """ Evaluates CPU mask used as decision for the apply() """
        self.topology = Topology(lscpu_output=self.lscpu())
        if not any([self.options.socket is not None, self.options.cpus, self.options.cpu_mask]):
            self.socket_detect()
        self.mask_detect()

    def apply(self, decision):
        """
        :param decision: queue list to write cpu mask
        """
        if len(decision) > 1 and not self.options.force:
            print('Skipped modifying {0} on {1} because it is multi-queue device (use --force flag to skip this check)'
                  .format(self.target, self.options.dev))
            exit(0)
        queue_dir = '/sys/class/net/{0}/queues/'.format(self.options.dev)
        for queue in decision:
            print_("Using mask '{0}' for {1}-{2}".format(self.options.cpu_mask, self.options.dev, queue))
            if self.options.dry_run:
                continue
            with open(os.path.join(queue_dir, queue, self.target), 'w') as queue_file:
                queue_file.write(self.options.cpu_mask)

    def parse_options(self):
        """
        :return: options for AutoRPS
        """
        parser = CPUBasedTune.make_parser()
        parser.add_argument('-f', '--force', help='Work even in case of multiqueue CPU', action='store_true',
                            default=False)
        parser.add_argument('-m', '--cpu-mask', help='Explicitly define mask to write in {0}'.format(self.target),
                            type=str)
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
        return hex(int(''.join([str(cpu) for cpu in bitmap]), 2))[2:]  # no need to write 0x

    def cpus_sys_local(self):
        cpus_local_file = '/sys/class/net/{0}/device/local_cpus'.format(self.options.dev)
        if not os.path.isfile(cpus_local_file):
            return
        with open(cpus_local_file, 'r') as fd:
            return fd.read().strip()

    def mask_detect(self):
        """
        Finds a way to calculate CPU mask to apply:
        1. --cpu-mask
        2. --cpus
        3. topology.layout
        """
        mask = None
        if self.options.cpu_mask:
            return
        if not self.options.cpus:
            mask = self.cpus_sys_local()
            if mask:
                self.options.cpu_mask = mask
            else:
                self.options.cpus = self.cpus_detect_real()
        if not mask:
            self.options.cpu_mask = self.cpus2mask(self.options.cpus, len(self.topology.socket_layout.keys()))

    def detect_queues_real(self):
        """
        :return: queue list to write cpu mask found by really reading /sys/
        """
        queue_dir = '/sys/class/net/{0}/queues/'.format(self.options.dev)
        return [queue for queue in os.listdir(queue_dir) if queue.startswith(self.queue_prefix)]

    def lscpu(self):
        """
        :return: `lscpu -p` output if test dir given (need for NUMA-node)
        """
        if not self.options.test_dir:
            return
        lscpu_output_filename = os.path.join(self.options.test_dir, "lscpu_output")
        lscpu_output = open(lscpu_output_filename).read()
        return str(lscpu_output) if isinstance(lscpu_output, bytes) else lscpu_output


class AutoXPS(AutoSoftirqTune):
    """ Allows to use multi-cpu packets processing for budget NICs """
    target = 'xps_cpus'
    queue_prefix = 'tx'


class AutoRPS(AutoSoftirqTune):
    """ Allows to use multi-cpu packets processing for budget NICs """
    target = 'rps_cpus'
    queue_prefix = 'rx'
