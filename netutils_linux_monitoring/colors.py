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

ColorsSocket = {
    0: Colors['OKBLUE'],
    1: Colors['WARNING'],
    2: Colors['FAIL'],
    3: Colors['OKGREEN'],
    -1: Colors['ENDC']
}


def __choose_color_scheme(numa):
    return ColorsNode if numa.layout_kind == 'NUMA' else ColorsSocket


def cpu_color(cpu, numa, color_scheme=None):
    if not color_scheme:
        color_scheme = __choose_color_scheme(numa)
    if isinstance(cpu, str):
        cpu = int(cpu[3:])
    return color_scheme.get(numa.layout.get(cpu))


def colorize_cpu_list(cpu_list, numa):
    """ return list of highlighted strings with CPU names regarding to NUMA """
    color_scheme = __choose_color_scheme(numa)
    return [cpu_color(cpu, numa, color_scheme) + cpu + Colors['ENDC'] for cpu in cpu_list]
