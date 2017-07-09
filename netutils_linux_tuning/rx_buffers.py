from os import system, path
from subprocess import Popen, PIPE

from six import print_


class RxBuffersIncreaser(object):

    """
    0. Check if buffers already been setted up in ifcfg-ethX
    1. Determines what size of buffers available
    2. Evaluate one that fits for our purposes
    3. Apply it
    """

    def __init__(self, dev=None, upper_bound=2048):
        self.dev = dev
        self.upper_bound = upper_bound
        self.current = 0
        self.maximum = 0
        self.prefered = None
        self.manual_tuned = False

    def __str__(self):
        attrs = ('dev', 'upper_bound', 'current', 'maximum', 'prefered')
        return str(dict((attr, self.__getattribute__(attr)) for attr in attrs))

    def investigate(self):
        """ get maximum and current rx ring buffers values via ethtool """
        def extract_value(line):
            return int(line.strip('RX:\t\n'))

        # We need to be sure that on RHEL system we don't automatically tune buffers
        # that have been already manually tuned. In non RHEL system we skip this checks.
        network_scripts = '/etc/sysconfig/network-scripts/'
        if path.exists(network_scripts):  # don't check ifcfg on non RHEL-based systems.
            config_file = path.join(network_scripts, 'ifcfg-' + self.dev)
            if path.exists(config_file):
                with open(config_file) as config:
                    if any(line for line in config.readlines() if 'ETHTOOL_OPTS' in line):
                        print_("{0}'s RX ring buffer already manually tuned.".format(self.dev))
                        exit(0)
        process = Popen(['ethtool', '-i', self.dev], stdout=PIPE, stderr=PIPE)
        _, _ = process.communicate()
        # silent fail if called for vlan/bridge/etc
        if process.returncode != 0:
            exit(0)
        process = Popen(['ethtool', '-g', self.dev], stdout=PIPE, stderr=PIPE)
        ethtool_buffers, _ = process.communicate()
        if process.returncode != 0:
            exit(1)
        ethtool_buffers = ethtool_buffers.split('\n')
        self.maximum = extract_value(ethtool_buffers[2])
        self.current = extract_value(ethtool_buffers[7])

    def determine(self, current=None, maximum=None):
        """ evaluate most fitting RX ring buffer's fize """
        if not current:
            current = self.current
        if not maximum:
            maximum = self.maximum
        if current > self.upper_bound:
            return current
        if maximum < self.upper_bound:
            return maximum
        return max(current, min(self.upper_bound, maximum / 2))

    def apply(self):
        """ doing all the job, applying new buffer's size if required """
        self.investigate()
        self.prefered = self.determine()
        if self.prefered == self.current:
            print_("{0}'s RX ring buffer already has fine size.".format(self.dev))
            return
        assert self.prefered, "Can't eval prefered RX ring buffer size."
        command = 'ethtool -G {0} rx {1}'.format(self.dev, self.prefered)
        print_('run:', command)
        system(command)
