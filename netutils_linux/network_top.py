#!/usr/bin/env python

from optparse import OptionParser, OptionConflictError
from base_top import BaseTop
from irqtop import IrqTop
from softirqs import Softirqs
from softnet_stat import SoftnetStatTop
from link_rate import LinkRateTop


class NetworkTop(BaseTop):
    def __init__(self):
        BaseTop.__init__(self)
        self.tops = {
            'irqtop': IrqTop(),
            'softnet_stat_top': SoftnetStatTop(),
            'softirq_top': Softirqs(),
            'link-rate': LinkRateTop(),
        }
        self.parse_options()

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
        repr_source = top.diff if top.options.delta_mode else top.current
        output = ["# network devices\n"]
        for dev in top.options.devices:
            output.append("{0:<14} {1}".format(dev, top.__repr_dev__(dev)))
        return "\n".join(output)

    def __repr_irq(self):
        top = self.tops.get('irqtop')
        repr_source = top.diff if top.options.delta_mode else top.current
        if not top.diff_total:
            return ""
        # output_lines = ["\t".join(str(x) for x in ['Total:'] + map(str, top.diff_total))]
        output_lines = list()
        for line in repr_source:
            if line[0] == 'CPU0':
                line.insert(0, ' ')
            elif top.skip_zero_line(line):
                continue
            output_lines.append("\t".join(map(str, line)))
        return "\n".join(["# /proc/interrupts\n"] + output_lines)

    def __repr_cpu(self):
        irqtop = self.tops.get('irqtop')
        softirq_top = self.tops.get('softirq_top')
        softnet_stat_top = self.tops.get('softnet_stat_top')

        # all these evaluations are better to put in softirqs.parse()
        softirq_repr_source = softirq_top.diff if softirq_top.options.delta_mode else softirq_top.current
        active_cpu_count = softirq_top.__active_cpu_count__(softirq_top.current)
        softirq_output = softirq_repr_source.get('NET_RX')[:active_cpu_count]
        softnet_stat_top_output = softnet_stat_top.diff if softnet_stat_top.options.delta_mode else softnet_stat_top.current

        network_output = zip(irqtop.diff_total, softirq_output, softnet_stat_top_output)
        fields = ["CPU", "Interrupts", "NET RX", "total", "dropped", "time_squeeze", "cpu_collision", "received_rps"]
        header = "# Load per cpu:\n\n{0:6}  {1:>12} {2:>12} {3:>12} {4:>8} {5:>12} {6:>13} {7:>12}".format(*fields)
        output = [header] + [
            "CPU{0:3}: {1:>12} {2:>12} {3:>12} {4:>8} {5:>12} {6:>13} {7:>12}".format(softnet_stat.cpu, irq, softirq,
                                                                                      softnet_stat.total,
                                                                                      softnet_stat.dropped,
                                                                                      softnet_stat.time_squeeze,
                                                                                      softnet_stat.cpu_collision,
                                                                                      softnet_stat.received_rps)
            for irq, softirq, softnet_stat in network_output
        ]
        return "\n".join(output)

    def __repr__(self):
        # return "\n".join(str(_top) for top_name, _top in self.tops.iteritems())
        return "\n\n".join([
            self.header,
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
        self.options, args = parser.parse_args()
        for top in self.tops.itervalues():
            top.options = self.options
            if hasattr(top, 'post_optparse'):
                top.post_optparse()


if __name__ == '__main__':
    NetworkTop().run()
