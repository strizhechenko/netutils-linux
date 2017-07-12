from colorama import Fore, Style

try:
    YELLOW = Fore.LIGHTYELLOW_EX
except AttributeError:
    YELLOW = Fore.YELLOW

COLORS_NODE = {
    0: Fore.GREEN,
    1: Fore.RED,
    2: YELLOW,
    3: Fore.BLUE,
    -1: Style.RESET_ALL,
}

COLORS_SOCKET = {
    0: Fore.BLUE,
    1: YELLOW,
    2: Fore.RED,
    3: Fore.GREEN,
    -1: Style.RESET_ALL,
}


class State(object):
    """ I'd like to use enum from py34+, but I need support for py26 and afraid to use enum34 from PYPI """
    OK = 0
    WARNING = 1
    ERROR = 2

    @staticmethod
    def fsm(value, warning, error):
        """ Nice place to apply FSM later """
        return State.ERROR if value >= error else State.WARNING if value >= warning else State.OK


class Metric(State):
    """
    In these utils exist a lot of metrics.
    Many of them have warning/error threshold and need to be highlighted
    """

    value = None
    warning = None
    error = None

    state = State.OK
    colors = {
        State.OK: Fore.RESET,
        State.ERROR: Fore.RED,
        State.WARNING: YELLOW
    }

    def __init__(self):
        self.text = self.colorize()

    def init(self, value):
        """ :returns: initialized object (assuming you inherited Metric) """
        assert self.warning is not None and self.error is not None
        self.__set_value(value)
        self.state = State.fsm(value, self.warning, self.error)
        return self

    def init_raw(self, value, warning, error):
        """ :returns: initialized object with ready-to-use thresholds """
        self.__set_warning(warning)
        self.__set_error(error)
        return self.init(value)

    def __set_value(self, value):
        self.value = value

    def __set_warning(self, warning):
        self.warning = warning

    def __set_error(self, error):
        self.error = error

    def colorize(self):
        return wrap(self.value, Metric.colors[self.state])


def bright(string):
    return wrap(string, Style.BRIGHT)


def wrap_header(string):
    return wrap("# {0}\n".format(string), Style.BRIGHT)


def colorize(value, warning, error):
    """ Wrapper for Metric class for backward compatibility """
    return Metric().init_raw(value, warning, error).colorize()


def wrap(word, color):
    """ wrap string in given color """
    return "{0}{1}{2}".format(color, word, Style.RESET_ALL)


def __choose_color_scheme(numa):
    return COLORS_NODE if numa.layout_kind == 'NUMA' else COLORS_SOCKET


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
