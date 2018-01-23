#!/usr/bin/env python
# coding: utf-8

from six import iteritems, itervalues

from netutils_linux_monitoring import IrqTop, Softirqs, SoftnetStatTop, LinkRateTop
from netutils_linux_monitoring.base_top import BaseTop
from netutils_linux_monitoring.colors import Color
from netutils_linux_monitoring.layout import make_table
from netutils_linux_monitoring.topology import Topology


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
        self.topology = Topology(fake=self.options.random, lscpu_output=self.options.lscpu_output)
        self.color = Color(self.topology)
        for top in self.tops.values():
            top.topology = self.topology
            top.color = self.color

    def parse(self):
        """
        :return: dict with parsed results for each top-like object.
        """
        return dict((top_name, _top.parse()) for top_name, _top in iteritems(self.tops))

    def eval(self):
        """
        :return: evaluates diff for each top-like object.
        """
        if all((self.current, self.previous)):
            self.diff = dict((top_name, _top.diff) for top_name, _top in iteritems(self.tops))

    def tick(self):
        self.previous = self.current
        self.current = self.parse()
        for _top in itervalues(self.tops):
            _top.tick()
        self.eval()

    def __repr__(self):
        output = [
            BaseTop.header,
            self.__repr_irq(),
            self.__repr_cpu(),
            self.__repr_dev(),
        ]
        if not self.options.clear:
            del output[0]
        return '\n'.join(output)

    def parse_options(self):
        """ Tricky way to gather all options in one util without conflicts, parse them and do some logic after parse """
        parser = BaseTop.make_base_parser()
        for top in itervalues(self.tops):
            parser = top.make_parser(parser)
        self.options = parser.parse_args()
        if self.options.lscpu_output:
            self.options.lscpu_output = open(self.options.lscpu_output).read()
        for top in itervalues(self.tops):
            top.options = self.options
            if hasattr(top, 'post_optparse'):
                top.post_optparse()

    def __repr_dev(self):
        top = self.tops.get('link-rate')
        table = make_table(top.make_header(), top.align_map, top.make_rows())
        return self.color.wrap_header('Network devices') + str(table)

    def __repr_irq(self):
        top = self.tops.get('irqtop')
        output_lines, cpu_count = top.make_rows()
        align_map = top.make_align_map(cpu_count)
        table = make_table(output_lines[0], align_map, output_lines[1:])
        return self.color.wrap_header('/proc/interrupts') + str(table)

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
            'CPU', 'Interrupts', 'NET RX', 'NET TX',
            'total', 'dropped', 'time_squeeze', 'cpu_collision', 'received_rps',
        ]
        fields = [self.color.bright(word) for word in fields]
        rows = self.__repr_cpu_make_rows(irqtop, network_output, softirq_top, softnet_stat_top)
        table = make_table(fields, ['l'] + ['r'] * (len(fields) - 1), rows)
        return self.color.wrap_header('Load per cpu:') + str(table)

    def __repr_cpu_make_rows(self, irqtop, network_output, softirq_top, softnet_stat_top):
        return [
            [
                self.color.wrap('CPU{0}'.format(stat.cpu), self.color.colorize_cpu(stat.cpu)),
                irqtop.colorize_irq_per_cpu(irq),
                softirq_top.colorize_net_rx(net_rx),
                softirq_top.colorize_net_tx(net_tx),
                softnet_stat_top.colorize_total(stat.total),
                softnet_stat_top.colorize_dropped(stat.dropped),
                softnet_stat_top.colorize_time_squeeze(stat.time_squeeze),
                softnet_stat_top.colorize_cpu_collision(stat.cpu_collision),
                stat.received_rps
            ]
            for irq, net_rx, net_tx, stat in network_output
        ]
