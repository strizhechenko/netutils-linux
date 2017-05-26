#!/usr/bin/env python

from top import Top
from irqtop import IrqTop
from softirqs import Softirqs
from softnet_stat import SoftnetStatTop
# from link_rate import LinkRateTop


class NetworkTop(Top):
    def __init__(self):
        Top.__init__(self, None)
        self.tops = {
            'irqtop': IrqTop(),
            'softnet_stat_top': SoftnetStatTop(),
            'softirq_top': Softirqs(),
            # 'link-rate': LinkRateTop(),
        }

    def parse(self):
        print 'parse called'
        return dict((top_name, _top.parse()) for top_name, _top in self.tops.iteritems())

    def eval(self):
        if all((self.current, self.previous)):
            self.diff = dict((top_name, _top.diff) for top_name, _top in self.tops.iteritems())

    def tick(self):
        print 'tick called'
        self.previous = self.current
        self.current = self.parse()
        for _top in self.tops.itervalues():
            _top.tick()
        self.eval()

    def __repr__(self):
        return "\n".join(str(_top) for top_name, _top in self.tops.iteritems())


if __name__ == '__main__':
    NetworkTop().run()
