#!/usr/bin/env python

from os import system
from time import sleep
from copy import deepcopy


def delta_print(old, new):
    old = map(str.strip, old)
    new = map(str.strip, new)
    for i in range(len(new)):
        _new = new[i].split()
        _old = old[i].split()
	line = [str(int(_new[i])-int(_old[i])) if _new[i].isdigit() else _new[i] for i in range(len(_new))]
        try:
            if len(line) == 2:
                print "{0:30} {1:10}".format(*line)
            else:
                print "{0:30} {1:10} {2:5}".format(*line)
	except IndexError as err:
            pass

def main():
    prev = None
    while True:
        with open('/proc/meminfo', 'r') as fd:
            new = fd.readlines()
        if prev is None:
            prev = deepcopy(new)
            continue
        sleep(1)
        system('clear')
        delta_print(prev, new)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt as err:
        exit(0)
