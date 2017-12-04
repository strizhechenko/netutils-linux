# coding: utf-8

"""
0. Check if buffers already been setted up in ifcfg-ethX
1. Determines what size of buffers available
2. Evaluate one that fits for our purposes
3. Apply it
"""

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
        if args and 'test' in args:
            return
        self.parse()
        self.apply(self.eval())

    def __str__(self):
        attrs = ('dev', 'upper_bound', 'current', 'maximum', 'prefered')
        return str(dict((attr, self.__getattribute__(attr)) for attr in attrs))

    def parse(self):
        """ get maximum and current rx ring buffers values via ethtool """
        self.network_scripts_check()
        self.run_ethtool('-i', 1)
        self.maximum, self.current = self.parse_ethtool_buffers()

    def eval(self):
        """ Just wrapper for static function """
        return self.eval_prefered_size(self.current, self.maximum, self.options.upper_bound)

    def apply(self, decision):
        """ doing all the job, applying new buffer's size if required """
        if decision == self.current:
            print_("{0}'s RX ring buffer already has fine size {1}.".format(self.options.dev, self.current))
            return
        assert decision, "Can't eval prefered RX ring buffer size."
        command = 'ethtool -G {0} rx {1}'.format(self.options.dev, decision)
        print_('run:', command)
        if not self.options.dry_run:
            system(command)

    @staticmethod
    def parse_options():
        """
        :return: parsed options for RxBuffersTune
        """
        parser = BaseTune.make_parser()
        parser.add_argument('-u', '--upper-bound', help='Work even in case of multi-queue CPU', type=int, default=2048)
        parser.add_argument('dev', type=str)
        return parser.parse_args()

    def run_ethtool(self, key, exit_code):
        """
        :param key: key to pass to ethtool command
        :param exit_code: if command fails, what code to return?
        :return: stdout of ethtool command
        """
        process = Popen(['ethtool', key, self.options.dev], stdout=PIPE, stderr=PIPE)
        stdout, _ = process.communicate()
        if process.returncode != 0:
            exit(exit_code)
        return stdout

    def parse_ethtool_buffers(self):
        """
        Dies if NIC doesn't support RX buffers size change
        :return: maximum_size, current_size
        """

        def line_value(number):
            """ extracts integer value from line with given number """
            return int(ethtool_buffers[number].strip('RX:\t'))

        ethtool_buffers = self.run_ethtool('-g', 1).split('\n')
        return line_value(2), line_value(7)

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
