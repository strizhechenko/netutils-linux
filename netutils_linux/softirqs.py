from optparse import Option
from netutils_linux.base_top import BaseTop


class Softirqs(BaseTop):
    """ Utility for monitoring software interrupts distribution """
    def __init__(self):
        BaseTop.__init__(self)
        specific_options = [
            Option('--softirqs-file', default='/proc/softirqs',
                   help='Option for testing on MacOS purpose.')
        ]
        self.specific_options.extend(specific_options)

    def parse(self):
        with open(self.options.softirqs_file) as fd:
            metrics = [line.strip().split(':')
                       for line in fd.readlines() if ':' in line]
            return dict((k, map(int, v.strip().split())) for k, v in metrics)

    @staticmethod
    def __active_cpu_count__(data):
        return len([metric for metric in data.get('TIMER') if metric > 0])

    def eval(self):
        self.diff = dict((key, self.list_diff(
            data, self.previous[key])) for key, data in self.current.iteritems())

    def __repr__(self):
        active_cpu_count = self.__active_cpu_count__(self.current)
        net_rx_active_cpu = self.repr_source().get('NET_RX')[:active_cpu_count]
        net_rx = ["CPU{0}: {1}".format(cpu, softirq)
                  for cpu, softirq in enumerate(net_rx_active_cpu)]
        return "\n".join(map(str, [self.header] + net_rx))


if __name__ == '__main__':
    Softirqs().run()
