# coding: utf-8

"""
0. Check if buffers already been setted up in ifcfg-ethX
1. Determines what size of buffers available
2. Evaluate one that fits for our purposes
3. Apply it
"""

from argparse import ArgumentParser
from os import system, path
from subprocess import Popen, PIPE

from six import print_

from netutils_linux_tuning.base_tune import BaseTune


class RxBuffersTune(BaseTune):
    """ Tune utility for RX buffers of NIC """

    prefered = None
    current = 0
    maximum = 0
    manual_tuned = False

    def __init__(self, args=None):
        BaseTune.__init__(self)
        if 'test' in args:
            return
        self.parse()
        self.apply(self.eval())

    def __str__(self):
        attrs = ('dev', 'upper_bound', 'current', 'maximum', 'prefered')
        return str(dict((attr, self.__getattribute__(attr)) for attr in attrs))

    def parse(self):
        """ get maximum and current rx ring buffers values via ethtool """
        self.network_scripts_check()
        self.vlan_check()
        self.maximum, self.current = self.parse_ethtool_buffers()

    def eval(self):
        """ Just wrapper for static function """
        return self.eval_prefered_size(self.current, self.maximum, self.options.upper_bound)

    def apply(self, prefered):
        """ doing all the job, applying new buffer's size if required """
        if prefered == self.current:
            print_("{0}'s RX ring buffer already has fine size.".format(self.options.dev))
            return
        assert self.prefered, "Can't eval prefered RX ring buffer size."
        command = 'ethtool -G {0} rx {1}'.format(self.options.dev, self.prefered)
        print_('run:', command)
        if not self.options.dry_run:
            system(command)

    @staticmethod
    def parse_options():
        """
        :return: parsed options for RxBuffersTune
        """
        parser = ArgumentParser()
        parser.add_argument('-t', '--test', type=str,
                            help="Just initialize RXBuffersTune object for test.")
        parser.add_argument('-d', '--dry-run', help="Don't write anything to smp_affinity_list.",
                            action='store_true', default=False)
        parser.add_argument('-u', '--upper-bound', help="Work even in case of multi-queue CPU", type=int, default=2048)
        parser.add_argument('dev', type=str)
        return parser.parse_args()

    def parse_ethtool_buffers(self):
        """
        Dies if NIC doesn't support RX buffers size change
        :return: maximum_size, current_size
        """
        process = Popen(['ethtool', '-g', self.options.dev], stdout=PIPE, stderr=PIPE)
        ethtool_buffers, _ = process.communicate()
        if process.returncode != 0:
            exit(1)
        ethtool_buffers = ethtool_buffers.split('\n')
        return int(ethtool_buffers[2].strip('RX:\t\n')), int(ethtool_buffers[7].strip('RX:\t\n'))

    def vlan_check(self):
        """ silent fail if called for vlan/bridge/etc """
        process = Popen(['ethtool', '-i', self.options.dev], stdout=PIPE, stderr=PIPE)
        _, _ = process.communicate()
        if process.returncode != 0:
            exit(0)

    def network_scripts_check(self):
        """
        We need to be sure that on RHEL system we don't automatically tune buffers
        that have been already manually tuned. In non RHEL system we skip this checks.
        """
        network_scripts = '/etc/sysconfig/network-scripts/'
        if not path.exists(network_scripts):
            return
        config_file = path.join(network_scripts, 'ifcfg-' + self.options.dev)
        if not path.exists(config_file):
            return
        with open(config_file) as config:
            if not any(line for line in config.readlines() if 'ETHTOOL_OPTS' in line):
                return
        print_("{0}'s RX ring buffer already manually tuned.".format(self.options.dev))
        exit(0)

    @staticmethod
    def eval_prefered_size(current, maximum, upper_bound):
        """
        :return: really calculates the prefered size of RX buffers
        """
        if current > upper_bound:
            return current
        if maximum < upper_bound:
            return maximum
        return max(current, min(upper_bound, maximum / 2))
