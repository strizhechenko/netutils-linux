from os import getenv, system
from time import sleep


class Top:
    current = None
    previous = None
    diff = None
    header = "Press CTRL-C to exit...\n"

    def __init__(self, filename):
        self.filename = filename
        self.interval = int(getenv('INTERVAL', 1))
        self.iterations = int(getenv('ITERATIONS', 60))
        self.no_delta = bool(int(getenv('NO_DELTA', 0)))

    def tick(self):
        self.previous = self.current
        self.current = self.parse()
        if all((self.previous, self.current)):
            self.eval()

    @staticmethod
    def list_diff(current, previous):
        return [data - previous[n] for n, data in enumerate(current)]

    def run(self):
        try:
            while self.iterations > -1:
                self.iterations -= 1
                sleep(self.interval)
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

    def parse(self):
        raise NotImplementedError

    def eval(self):
        raise NotImplementedError

    def __repr__(self):
        raise NotImplementedError
