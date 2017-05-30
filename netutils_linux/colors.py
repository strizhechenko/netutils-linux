from numa import Numa
from random import sample

Colors = {
    "GREY": '\033[90m',
    "HEADER": '\033[95m',
    "OKBLUE": '\033[94m',
    "OKGREEN": '\033[92m',
    "WARNING": '\033[93m',
    "FAIL": '\033[91m',
    "ENDC": '\033[0m',
    "BOLD": '\033[1m',
    "UNDERLINE": '\033[4m',
}

ColorsNode = {
    0: Colors['OKGREEN'],
    1: Colors['FAIL'],
    2: Colors['WARNING'],
    3: Colors['OKBLUE'],
    -1: Colors['ENDC']
}


def colorize_cpu_list(cpu_list, numa):
    return [ColorsNode.get(numa.cpu_node(int(cpu[3:]))) + cpu + Colors['ENDC'] for cpu in cpu_list]


def get_random_color():
    return sample(ColorsNode.values(), 1)[0]


if __name__ == '__main__':
    CPU_LIST = ['CPU{0}'.format(i) for i in xrange(32)]
    # ['CPU0', 'CPU1', 'CPU2', 'CPU3', 'CPU4', 'CPU5', 'CPU6', 'CPU7']
    print " ".join(colorize_cpu_list(CPU_LIST, Numa(fake=True)))
