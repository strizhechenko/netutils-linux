from os import system
from time import sleep
from random import randint
from optparse import Option, OptionParser, OptionConflictError


class BaseTop:
    """ Base class for all these top-like utils. """
    current = None
    previous = None
    diff = None
    header = "Press CTRL-C to exit...\n"
    options = None

    def __init__(self):
        """
        Base __init__() should only list common options that will be used in all specific top-like utils.
        All specific top-like utils should extend, but NOT OVERRIDE self.specific_options.
        """
        self.specific_options = [
            Option('-i', '--interval', default=1, type=int, help='Interval between screen renew in seconds.'),
            Option('-n', '--iterations', dest='iterations', default=60, type=int,
                   help="Count of screen's renews, -1 - infinite loop."),
            Option('--no-delta-mode', action='store_false', dest='delta_mode', default=True,
                   help="Shows metrics' values instead of growth."),
            Option('--no-delta-small-hide', action='store_false', dest='delta_small_hide', default=True,
                   help="Prevent lines with only small changes or without changes at all from hiding."),
            Option('-l', '--delta-small-hide-limit', default=80, type=int,
                   help='Hides lines with only changes less than this limit'),
            Option('--no-color', dest='color', default=True, action='store_false',
                   help="Don't highlight NUMA nodes or sockets"),
            Option('--spaces', default=False, action='store_true',
                   help="Add spaces in numbers' representation, e.g. '1234567' will be '1 234 567'"),
            Option('--random', default=False, action='store_true',
                   help="Shows random diff data instead of real evaluation. Helpful for testing on static files")
        ]

    def parse_options(self):
        """ That should be explicitly called in __main__ part of any top-like utils """
        parser = OptionParser()
        for opt in self.specific_options:
            try:
                parser.add_option(opt)
            except OptionConflictError:
                pass
        self.options, args = parser.parse_args()
        if hasattr(self, 'post_optparse'):
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
                system('clear')
                if self.diff:
                    print self
        except KeyboardInterrupt:
            print
            exit(0)

    @staticmethod
    def int(item):
        return int(item) if item.isdigit() else item

    def spaces(self, n, sep=' '):
        if not self.options.spaces:
            return n
        output = str()
        while n / 1000 > 0:
            output = str(n % 1000).zfill(3) + sep + output
            n /= 1000
        return (str(n % 1000) + sep + output).strip()

    def parse(self):
        raise NotImplementedError

    def eval(self):
        raise NotImplementedError

    def __repr__(self):
        raise NotImplementedError
