from colorama import Fore, Style


ColorsNode = {
    0: Fore.GREEN,
    1: Fore.RED,
    2: Fore.LIGHTYELLOW_EX,
    3: Fore.BLUE,
    -1: Style.RESET_ALL,
}

ColorsSocket = {
    0: Fore.BLUE,
    1: Fore.LIGHTYELLOW_EX,
    2: Fore.RED,
    3: Fore.GREEN,
    -1: Style.RESET_ALL,
}


def wrap_header(string):
    return wrap("# {0}\n".format(string), Style.BRIGHT)


def colorize(value, warning, error):
    return wrap(value, Fore.RED if value >= error else Fore.LIGHTYELLOW_EX if value >= warning else Fore.RESET)


def wrap(word, color):
    """ wrap string in given color """
    return "{0}{1}{2}".format(color, word, Style.RESET_ALL)


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
