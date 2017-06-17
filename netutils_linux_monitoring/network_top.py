#!/usr/bin/env python

from colorama import Style
from optparse import OptionParser, OptionConflictError
from netutils_linux_monitoring import IrqTop, Softirqs, SoftnetStatTop, LinkRateTop
from netutils_linux_monitoring.numa import Numa
from netutils_linux_monitoring.base_top import BaseTop
from netutils_linux_monitoring.colors import cpu_color, wrap, colorize, wrap_header
from netutils_linux_monitoring.layout import make_table


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
            self.diff = dict((top_name, _top.diff) for top_name, _top in self.tops.iteritems())

    def tick(self):
        self.previous = self.current
        self.current = self.parse()
        for _top in self.tops.itervalues():
            _top.tick()
        self.eval()

    def __repr_dev(self):
        top = self.tops.get('link-rate')
        table = make_table(top.make_header(), top.align_map, top.make_rows())
        return wrap_header("Network devices") + str(table)

    def __repr_irq(self):
        top = self.tops.get('irqtop')
        output_lines, cpu_count = top.make_rows()
        align_map = top.make_align_map(cpu_count)
        table = make_table(output_lines[0], align_map, output_lines[1:])
        return wrap_header("/proc/interrupts") + str(table)

    def __repr_cpu(self):
        irqtop = self.tops.get('irqtop')
        softirq_top = self.tops.get('softirq_top')
        softnet_stat_top = self.tops.get('softnet_stat_top')
        # all these evaluations are better to put in softirqs.parse()
        active_cpu = softirq_top.__active_cpu_count__(
            softirq_top.current)
        softnet_stat_top_output = softnet_stat_top.repr_source()
        network_output = zip(irqtop.diff_total,
                             softirq_top.repr_source()['NET_RX'][:active_cpu],
                             softirq_top.repr_source()['NET_TX'][:active_cpu],
                             softnet_stat_top_output)
        fields = [
            "CPU", "Interrupts", "NET RX", "NET TX",
            "total", "dropped", "time_squeeze", "cpu_collision", "received_rps",
        ]
        fields = [wrap(word, Style.BRIGHT) for word in fields]
        rows = self.__repr_cpu_make_rows(irqtop, network_output, softirq_top, softnet_stat_top)
        table = make_table(fields, ['l'] + ['r'] * (len(fields) - 1), rows)
        return wrap_header("Load per cpu:") + str(table)

    def __repr_cpu_make_rows(self, irqtop, network_output, softirq_top, softnet_stat_top):
        rows = [
            [
                wrap("CPU{0}".format(stat.cpu), cpu_color(stat.cpu, self.numa)),
                colorize(irq, irqtop.irq_warning, irqtop.irq_error),
                colorize(softirq_rx, softirq_top.net_rx_warning, softirq_top.net_rx_error),
                colorize(softirq_tx, softirq_top.net_tx_warning, softirq_top.net_tx_error),
                colorize(stat.total, softnet_stat_top.total_warning, softnet_stat_top.total_error),
                colorize(stat.dropped, softnet_stat_top.dropped_warning, softnet_stat_top.dropped_error),
                colorize(stat.time_squeeze, softnet_stat_top.time_squeeze_warning, softnet_stat_top.time_squeeze_error),
                colorize(stat.cpu_collision, softnet_stat_top.cpu_collision_warning,
                         softnet_stat_top.cpu_collision_error),
                stat.received_rps
            ]
            for irq, softirq_rx, softirq_tx, stat in network_output
        ]
        return rows

    def __repr__(self):
        output = [
            BaseTop.header,
            self.__repr_irq(),
            self.__repr_cpu(),
            self.__repr_dev(),
        ]
        if not self.options.clear:
            del output[0]
        return "\n".join(output)

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
