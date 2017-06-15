from os import system
from time import sleep
from random import randint
from optparse import Option, OptionParser, OptionConflictError
from colorama import Fore
from colors import wrap


class BaseTop(object):
    """ Base class for all these top-like utils. """
    current = None
    previous = None
    diff = None
    header = wrap("Press CTRL-C to exit...\n", Fore.LIGHTBLACK_EX)
    options = None

    def __init__(self):
        """
        Base __init__() should only list common options that will be used in
        all specific top-like utils. All specific top-like utils should extend,
        but NOT OVERRIDE self.specific_options.
        """
        self.specific_options = [
            Option('-i', '--interval', default=1, type=int,
                   help='Interval between screen renew in seconds.'),
            Option('-n', '--iterations', dest='iterations', default=60, type=int,
                   help="Count of screen's renews, -1 - infinite loop."),
            Option('--no-delta-mode', action='store_false', dest='delta_mode',
                   default=True, help="Shows metrics' values instead of growth."),
            Option('--no-delta-small-hide', action='store_false',
                   dest='delta_small_hide', default=True,
                   help="Prevent lines with only small changes or without"
                        "changes at all from hiding."),
            Option('-l', '--delta-small-hide-limit', default=80, type=int,
                   help='Hides lines with only changes less than this limit'),
            Option('--no-color', dest='color', default=True, action='store_false',
                   help="Don't highlight NUMA nodes or sockets"),
            Option('--spaces', default=False, action='store_true',
                   help="Add spaces in numbers' representation, e.g. '1234567' "
                        "will be '1 234 567'"),
            Option('--random', default=False, action='store_true',
                   help="Shows random diff data instead of real evaluation. "
                        "Helpful for testing on static files"),
            Option('--no-clear', default=True, dest='clear', action='store_false',
                   help="Don't clear screen after each iteration. May be useful in scripts/logging to file."),
        ]

    def parse_options(self, options=None):
        """ That should be explicitly called in __main__ part of any top-like utils """
        parser = OptionParser()
        for opt in self.specific_options:
            try:
                parser.add_option(opt)
            except OptionConflictError:
                pass
        self.options, _ = parser.parse_args()
        if options:
            for name, value in options.iteritems():
                setattr(self.options, name, value)
        if hasattr(self, 'post_optparse'):
            # pylint: disable=E1101
            self.post_optparse()

    def tick(self):
        """ Gathers new data + evaluate diff between current & previous data """
        self.previous = self.current
        self.current = self.parse()
        if all((self.previous, self.current)):
            self.eval()

    def list_diff(self, current, previous):
        """ It's strange that there is no [3,4,3] - [1,2,1] -> [2,2,2] in standard library """
        if self.options.random:
            return [randint(0, 10000) for _ in current]
        return [data - previous[n] for n, data in enumerate(current)]

    def run(self):
        """ Default main()-like function for specific top-like utils except meta-utils. """
        try:
            while self.options.iterations > -1:
                self.options.iterations -= 1
                sleep(self.options.interval)
                self.tick()
                if self.options.clear:
                    system('clear')
                if self.diff:
                    print self
        except KeyboardInterrupt:
            print
            exit(0)

    def repr_source(self):
        return self.diff if self.options.delta_mode else self.current

    @staticmethod
    def int(item):
        return int(item) if item.isdigit() else item

    def spaces(self, number, sep=' '):
        """ 1234567 -> 1 234 567 """
        if not self.options.spaces:
            return number
        output = str()
        while number / 1000 > 0:
            output = str(number % 1000).zfill(3) + sep + output
            number /= 1000
        return (str(number % 1000) + sep + output).strip()

    def __repr_table__(self, table):
        if self.options.clear:
            return BaseTop.header + str(table)
        return str(table)

    def parse(self):
        """ Should read some file(s) into python structure (dict/list) """
        raise NotImplementedError

    def eval(self):
        """ Should evaluate self.diff using self.previous / self.current """
        raise NotImplementedError

    def __repr__(self):
        """ Should return string, representing self.diff """
        raise NotImplementedError
