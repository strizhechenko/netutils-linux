#!/usr/bin/env python

from optparse import OptionParser, OptionConflictError
from netutils_linux_monitoring import IrqTop
from netutils_linux_monitoring import Softirqs
from netutils_linux_monitoring import SoftnetStatTop
from netutils_linux_monitoring import LinkRateTop
from netutils_linux_monitoring.numa import Numa
from netutils_linux_monitoring.base_top import BaseTop
from netutils_linux_monitoring.colors import cpu_color, colorize_cpu_list, Colors, ColorsNode


class NetworkTop(BaseTop):
    """ Global top-like util that combine information from 4 other tops """

    def __init__(self):
        BaseTop.__init__(self)
        self.tops = {
            'irqtop': IrqTop(),
            'softnet_stat_top': SoftnetStatTop(),
            'softirq_top': Softirqs(),
            'link-rate': LinkRateTop(),
        }
        self.parse_options()
        self.numa = Numa(devices=self.options.devices,
                         fake=self.options.random)
        self.numa.layout_kind = 'SOCKET' # TODO: remove

    def parse(self):
        return dict((top_name, _top.parse()) for top_name, _top in self.tops.iteritems())

    def eval(self):
        if all((self.current, self.previous)):
            self.diff = dict((top_name, _top.diff)
                             for top_name, _top in self.tops.iteritems())

    def tick(self):
        self.previous = self.current
        self.current = self.parse()
        for _top in self.tops.itervalues():
            _top.tick()
        self.eval()

    def __repr_dev(self):
        top = self.tops.get('link-rate')
        output = [Colors['BOLD'], "# Network devices",
                  top.make_header(network_top=True), Colors['ENDC']]
        for dev in top.options.devices:
            output.append("{0}{1:<14}{3} {2}".format(
                ColorsNode.get(self.numa.devices.get(dev)),
                dev, top.__repr_dev__(dev),
                Colors['ENDC']))
        return "\n".join(output)

    def __repr_irq(self):
        top = self.tops.get('irqtop')
        if not top.diff_total:
            return ""
        output_lines = list()
        for line in top.repr_source():
            if line[0] == 'CPU0':
                line = colorize_cpu_list(line, self.numa)
                line.insert(0, ' ')
            elif top.skip_zero_line(line):
                continue
            output_lines.append("\t".join(map(str, line)))
        return "\n".join([Colors['BOLD'] + "# /proc/interrupts\n" + Colors['ENDC']] + output_lines)

    def __repr_cpu(self):
        irqtop = self.tops.get('irqtop')
        softirq_top = self.tops.get('softirq_top')
        softnet_stat_top = self.tops.get('softnet_stat_top')
        # all these evaluations are better to put in softirqs.parse()
        active_cpu = softirq_top.__active_cpu_count__(
            softirq_top.current)
        softirq_rx = softirq_top.repr_source().get('NET_RX')[:active_cpu]
        softirq_tx = softirq_top.repr_source().get('NET_TX')[:active_cpu]
        softnet_stat_top_output = softnet_stat_top.repr_source()
        network_output = zip(irqtop.diff_total,
                             softirq_rx,
                             softirq_tx,
                             softnet_stat_top_output)
        fields = [
            Colors['BOLD'],
            "CPU",
            "Interrupts",
            "NET RX",
            "NET TX",
            "total",
            "dropped",
            "time_squeeze",
            "cpu_collision",
            "received_rps",
            Colors['ENDC'],
        ]
        header_template = "{0}# Load per cpu:\n\n{1:6}  {2:>12} {3:>12} {4:>12} {5:>12} {6:>8} {7:>12} {8:>13} {9:>12}{10}\n"
        cpu_row_template = "{0}CPU{1:<3}{2}: {3:>12} {4:>12} {5:>12} {6:>12} {7:>8} {8:>12} {9:>13} {10:>12}"
        header = header_template.format(*fields)
        output = [header] + [
            cpu_row_template.format(
                cpu_color(softnet_stat.cpu, self.numa),
                softnet_stat.cpu,
                Colors['ENDC'],
                irq, softirq_rx, softirq_tx,
                softnet_stat.total,
                softnet_stat.dropped,
                softnet_stat.time_squeeze,
                softnet_stat.cpu_collision,
                softnet_stat.received_rps)
            for irq, softirq_rx, softirq_tx, softnet_stat in network_output
        ]
        return Colors['ENDC'] + "\n".join(output) + Colors['ENDC']

    def __repr__(self):
        # return "\n".join(str(_top) for top_name, _top in self.tops.iteritems())
        return "\n\n".join([
            Colors['GREY'] + self.header + Colors['ENDC'],
            self.__repr_irq(),
            self.__repr_cpu(),
            self.__repr_dev(),
        ])

    def parse_options(self):
        parser = OptionParser()
        for top in self.tops.itervalues():
            for opt in top.specific_options:
                try:
                    parser.add_option(opt)
                except OptionConflictError:
                    pass  # I don't know how to make a set of options
        self.options, _ = parser.parse_args()
        for top in self.tops.itervalues():
            top.options = self.options
            if hasattr(top, 'post_optparse'):
                top.post_optparse()


if __name__ == '__main__':
    NetworkTop().run()
