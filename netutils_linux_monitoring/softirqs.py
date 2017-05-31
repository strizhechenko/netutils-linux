from optparse import Option
from netutils_linux_monitoring.base_top import BaseTop


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
        sub_header = "CPU         NET_RX     NET_TX\n"
        net_xx = zip(
            self.repr_source().get('NET_RX')[:active_cpu_count],
            self.repr_source().get('NET_TX')[:active_cpu_count])
        softirqs = ["CPU{0:<3}: {1:>10} {2:>10}".format(cpu, softirq[0], softirq[1]) for cpu, softirq in enumerate(net_xx)]
        return "\n".join(map(str, [self.header] + [sub_header] + softirqs))


if __name__ == '__main__':
    Softirqs().run()
