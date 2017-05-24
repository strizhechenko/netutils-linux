#!/usr/bin/env python

import os
import time
from irqtop import InterruptDiff
from softirqs import Softirqs
from softnet_stat import SoftnetStat


def loop(tops, interval=1):
    while True:
        for top in tops:
            top.eval()
        os.system('clear')
        print "Press CTRL-C to exit..."
        for top in tops:
            print top
        time.sleep(interval)

if __name__ == '__main__':
    loop((InterruptDiff(),))
