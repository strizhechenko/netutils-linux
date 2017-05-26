#!/usr/bin/env python

from top import Top
from irqtop import IrqTop
from softirqs import Softirqs
from softnet_stat import SoftnetStatTop


class NetworkTop(Top):
    def __init__(self):
        Top.__init__(self, None)
        self.tops = {
            'irqtop': IrqTop(),
            'softnet_stat_top': SoftnetStatTop(),
            'softirq_top': Softirqs(),
        }

    def parse(self):
        return dict((top_name, top.parse()) for top_name, top in self.tops.iteritems())

    def eval(self):
        for top in self.tops.itervalues():
            top.eval()

    def __repr__(self):
        return "\n".join(str(top) for top in self.tops)


if __name__ == '__main__':
    NetworkTop().run()
