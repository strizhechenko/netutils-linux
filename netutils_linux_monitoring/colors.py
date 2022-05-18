# coding: utf-8

from colorama import Fore, Style


class Color(object):
    """ Helper for highlighting a console tools """
    try:
        CLS_YELLOW = Fore.LIGHTYELLOW_EX
        CLS_GREY = Fore.LIGHTBLACK_EX
    except AttributeError:
        CLS_YELLOW = Fore.YELLOW
        CLS_GREY = Fore.CYAN

    COLORS_NODE = {
        0: Fore.GREEN,
        1: Fore.RED,
        2: CLS_YELLOW,
        3: Fore.BLUE,
        -1: Style.RESET_ALL,
    }

    COLORS_SOCKET = {
        0: Fore.BLUE,
        1: CLS_YELLOW,
        2: Fore.RED,
        3: Fore.GREEN,
        -1: Style.RESET_ALL,
    }

    COLOR_NONE = dict((key, "") for key in range(-1, 4))

    def __init__(self, topology, enabled):
        self.enabled, self.topology = enabled, topology
        self.RESET, self.RESET_ALL = Fore.RESET, Style.RESET_ALL
        self.YELLOW, self.GREY = Color.CLS_YELLOW, Color.CLS_GREY
        self.RED, self.BRIGHT = Fore.RED, Style.BRIGHT
        self.color_scheme = self.__choose_color_scheme()

    def __choose_color_scheme(self):
        if not self.enabled or not self.topology:
            self.BRIGHT = self.RESET_ALL = self.RED = self.RESET = self.GREY = self.YELLOW = ""
            return self.COLOR_NONE
        if self.topology.layout_kind == 'NUMA':
            return self.COLORS_NODE
        return self.COLORS_SOCKET

    def wrap(self, word, color):
        """ wrap string in given color """
        return '{0}{1}{2}'.format(color, word, self.RESET_ALL)

    def colorize(self, value, warning, error):
        return self.wrap(value, self.RED if value >= error else self.YELLOW if value >= warning else self.RESET)

    def bright(self, string):
        return self.wrap(string, self.BRIGHT)

    def wrap_header(self, string):
        return self.wrap("# {0}\n".format(string), self.BRIGHT)

    def colorize_cpu(self, cpu):
        if isinstance(cpu, str):
            cpu = int(cpu[3:])
        return self.color_scheme.get(self.topology.layout.get(cpu))

    def colorize_cpu_list(self, cpu_list):
        """ return list of highlighted strings with CPU names regarding to NUMA """
        return [self.wrap(cpu, self.colorize_cpu(cpu)) for cpu in cpu_list]
