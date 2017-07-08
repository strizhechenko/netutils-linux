# coding=utf-8

""" Receive Packet Steering tuning utility """
import os
from argparse import ArgumentParser

from six import print_, iteritems

from netutils_linux_monitoring.numa import Numa


class AutoRPS(object):
    def __init__(self):
        self.options = self.parse_options()
        self.numa = self.make_numa()
        self.process_options()
        self.mask_apply()

    def socket_detect(self):
        if any([self.options.socket, self.options.cpus, self.options.cpu_mask]):
            return
        socket = self.numa.node_dev_dict([self.options.dev], True).get(self.options.dev)
        self.options.socket = 0 if socket == -1 else socket

    def make_numa(self):
        return Numa(lscpu_output=self.read_test_dir())

    def read_test_dir(self):
        if self.options.test_dir:
            lscpu_output_filename = os.path.join(self.options.test_dir, "lscpu_output")
            lscpu_output = open(lscpu_output_filename).read()
            if isinstance(lscpu_output, bytes):
                lscpu_output = str(lscpu_output)
            return lscpu_output

    def detect_cpus(self):
        self.options.cpus = [k for k, v in iteritems(self.numa.socket_layout) if v == self.options.socket]

    @staticmethod
    def cpus2mask(cpus, cpus_count):
        """ There's no need to fill mask with zeroes, kernel does it automatically """
        bitmap = [0] * cpus_count
        for cpu in cpus:
            bitmap[cpu] = 1
        return hex(int("".join(map(str, bitmap)), 2))[2:]

    def mask_detect(self):
        if self.options.cpu_mask:
            return
        if not self.options.cpus:
            self.detect_cpus()
        self.options.cpu_mask = self.cpus2mask(self.options.cpus, len(self.numa.socket_layout.keys()))

    def process_options(self):
        self.socket_detect()
        self.mask_detect()

    def detect_queues(self, queue_dir):
        return [queue for queue in os.listdir(queue_dir) if queue.startswith('rx')]

    def mask_apply(self):
        if self.options.test_dir:
            self.mask_apply_test()
        queue_dir = "/sys/class/net/{0}/queues/".format(self.options.dev)
        queues = self.detect_queues(queue_dir)
        if len(queues) > 1 and not self.options.force:
            raise OSError("Refuse to use RPS on multiqueue NIC. You may use --force flag to apply RPS for all queues")
        for queue in queues:
            print_("Using mask '{0}' for {1}-{2}".format(self.options.cpu_mask, self.options.dev, queue))
            if self.options.dry_run:
                continue
            with open(os.path.join(queue_dir, queue, 'rps_cpus'), 'w') as queue_file:
                queue_file.write(self.options.cpu_mask)

    @staticmethod
    def parse_options():
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
