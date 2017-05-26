#!/usr/bin/env python

from top import Top
from irqtop import IrqTop
from softirqs import Softirqs
from softnet_stat import SoftnetStatTop


class NetworkTop(Top):
    def __init__(self):
        Top.__init__(self, None)

    def parse(self):
        pass

    def eval(self):
        pass

    def __repr__(self):
        pass


if __name__ == '__main__':
    NetworkTop().run()
