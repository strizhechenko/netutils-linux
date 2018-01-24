# coding: utf-8

from colorama import Fore, Style


class Color(object):
    """ Helper for highlighting a console tools """
    try:
        YELLOW = Fore.LIGHTYELLOW_EX
        GREY = Fore.LIGHTBLACK_EX
    except AttributeError:
        YELLOW = Fore.YELLOW
        GREY = Fore.CYAN

    COLORS_NODE = {
        0: Fore.GREEN,
        1: Fore.RED,
        2: YELLOW,
        3: Fore.BLUE,
        -1: Style.RESET_ALL,
    }
    COLORS_SOCKET = dict((key, COLORS_NODE[3 - key]) for key in range(0, 4))
    COLORS_SOCKET[-1] = COLORS_NODE[-1]
    COLOR_NONE = dict((key, "") for key in range(-1, 4))

    def __init__(self, topology):
        self.topology = topology
        if topology is not None:
            self.color_scheme = self.__choose_color_scheme()

    def __choose_color_scheme(self):
        return self.COLORS_NODE if self.topology.layout_kind == 'NUMA' else self.COLORS_SOCKET

    @staticmethod
    def wrap(word, color):
        """ wrap string in given color """
        return '{0}{1}{2}'.format(color, word, Style.RESET_ALL)

    @staticmethod
    def colorize(value, warning, error):
        return Color.wrap(value, Fore.RED if value >= error else Color.YELLOW if value >= warning else Fore.RESET)

    @staticmethod
    def bright(string):
        return Color.wrap(string, Style.BRIGHT)

    @staticmethod
    def wrap_header(string):
        return Color.wrap("# {0}\n".format(string), Style.BRIGHT)

    def colorize_cpu(self, cpu):
        if not self.color_scheme:
            self.color_scheme = self.__choose_color_scheme()
        if isinstance(cpu, str):
            cpu = int(cpu[3:])
        return self.color_scheme.get(self.topology.layout.get(cpu))

    def colorize_cpu_list(self, cpu_list):
        """ return list of highlighted strings with CPU names regarding to NUMA """
        return [self.wrap(cpu, self.colorize_cpu(cpu)) for cpu in cpu_list]
