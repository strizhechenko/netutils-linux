from os import getenv, system
from time import sleep


class Top:
    current = None
    previous = None
    diff = None
    header = "Press CTRL-C to exit..."

    def __init__(self, filename):
        self.filename = filename
        self.interval = int(getenv('INTERVAL', 1))
        self.iterations = int(getenv('ITERATIONS', 60))

    def tick(self):
        self.previous = self.current
        self.current = self.parse()
        if all((self.previous, self.current)):
            self.eval()

    def run(self):
        try:
            while self.iterations > -1:
                self.iterations -= 1
                sleep(self.interval)
                self.tick()
                system('clear')
                print self
        except KeyboardInterrupt:
            print
            exit(0)

    @staticmethod
    def __int(item):
        return int(item) if item.isdigit() else item

    def parse(self):
        raise NotImplementedError

    def eval(self):
        raise NotImplementedError

    def __repr__(self):
        raise NotImplementedError
