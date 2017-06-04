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
    0: 'OKGREEN',
    1: 'FAIL',
    2: 'WARNING',
    3: 'OKBLUE',
    -1: 'ENDC'
}

ColorsSocket = {
    0: 'OKBLUE',
    1: 'WARNING',
    2: 'FAIL',
    3: 'OKGREEN',
    -1: 'ENDC'
}


def colorize(value, warning, error):
    if value >= error:
        return wrap(value, 'FAIL')
    if value >= warning:
        return wrap(value, 'WARNING')
    return wrap(value, 'ENDC')

def wrap(word, color):
    """ wrap string in given color """
    return "{0}{1}{2}".format(Colors[color], word, Colors['ENDC'])


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
    return [wrap(cpu, cpu_color(cpu, numa, color_scheme)) for cpu in cpu_list]
