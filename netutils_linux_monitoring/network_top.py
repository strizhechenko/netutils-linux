#!/usr/bin/env python

from optparse import OptionParser, OptionConflictError
from netutils_linux_monitoring import IrqTop
from netutils_linux_monitoring import Softirqs
from netutils_linux_monitoring import SoftnetStatTop
from netutils_linux_monitoring import LinkRateTop
from netutils_linux_monitoring.numa import Numa
from netutils_linux_monitoring.base_top import BaseTop
from netutils_linux_monitoring.colors import cpu_color, colorize_cpu_list, ColorsNode, wrap, colorize


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
        output = [
            wrap("# Network devices", 'BOLD'),
            wrap(top.make_header(network_top=True), 'BOLD')
        ]
        for dev in top.options.devices:
            output.append("{0:<14}{1}".format(
                wrap(dev, ColorsNode.get(self.numa.devices.get(dev))),
                top.__repr_dev__(dev)))
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
        return "\n".join([wrap("# /proc/interrupts\n", 'BOLD')] + output_lines)

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
            "CPU",
            "Interrupts",
            "NET RX",
            "NET TX",
            "total",
            "dropped",
            "time_squeeze",
            "cpu_collision",
            "received_rps",
        ]
        header_template = "# Load per cpu:\n\n{0:6}  {1:>12} {2:>12} {3:>12} {4:>12} {5:>8} {6:>12} {7:>13} {8:>12}\n"
        cpu_row_template = "{0:<15} `{1:>22}` {2:>20} {3:>20} {4:>20} {5:>16} {6:>20} {7:>21} {8:>20} {9}"
        header = wrap(header_template.format(*fields), 'BOLD')
        output = [header] + [
            cpu_row_template.format(
                wrap("CPU{0}".format(softnet_stat.cpu), cpu_color(softnet_stat.cpu, self.numa)),
                colorize(irq, 40000, 80000),
                colorize(softirq_rx, 40000, 80000),
                colorize(softirq_tx, 20000, 30000),
                colorize(softnet_stat.total, 300000, 900000),
                colorize(softnet_stat.dropped, 1, 1),
                colorize(softnet_stat.time_squeeze, 1, 300),
                colorize(softnet_stat.cpu_collision, 1, 1000),
                softnet_stat.received_rps,
                len(colorize(irq, 40000, 80000)))
            for irq, softirq_rx, softirq_tx, softnet_stat in network_output
        ]
        return "\n".join(output)

    def __repr__(self):
        return "\n\n".join([
            wrap(self.header, 'GREY'),
            self.__repr_irq(),
            self.__repr_cpu(),
            self.__repr_dev(),
        ])

    def parse_options(self):
        """ Tricky way to gather all options in one util without conflicts, parse them and do some logic after parse """
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
