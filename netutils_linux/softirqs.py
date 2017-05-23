import os
import time


class Softirqs(object):
    def __init__(self, filename='/proc/softirqs'):
        self.filename = filename

    def file2data(self):
        with open(self.filename) as fd:
            metrics = [line.strip().split(':') for line in fd.readlines() if ':' in line]
            return dict((k, map(int, v.strip().split())) for k, v in metrics)

    @staticmethod
    def __active_cpu_count__(data):
        return len([metric for metric in data.get('TIMER') if metric > 0])

    @staticmethod
    def __list_diff__(cur, prev):
        return [cur[i] - prev[i] for i in xrange(len(cur))]

    @staticmethod
    def __list_print__(data):
        print "Press CTRL-C to exit..."
        print
        for n, v in enumerate(data):
            print 'CPU{0}: {1}'.format(n, v)

    def __loop__(self):
        net_rx = None
        while True:
            data = self.file2data()
            cpu_count = self.__active_cpu_count__(data)
            net_rx_cur = data.get('NET_RX')[:cpu_count]
            if net_rx:
                os.system('clear')
                self.__list_print__(self.__list_diff__(net_rx_cur, net_rx))
            net_rx = net_rx_cur
            time.sleep(1)

    def loop(self):
        try:
            self.__loop__()
        except KeyboardInterrupt as err:
            print
            exit(0)
