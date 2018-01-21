""" CPU/Memory specific things: NUMA, Sockets """

# coding: utf-8

from subprocess import Popen, PIPE
from sys import version_info

from six import print_

from netutils_linux_hardware.rate_math import any2int


class Topology(object):
    """ Dealing with NUMA/CPU nodes based on lscpu output """
    __FAKE_LAYOUT = {
        0: 0, 1: 0, 2: 0, 3: 0,
        4: 1, 5: 1, 6: 1, 7: 1,
        8: 0, 9: 0, 10: 0, 11: 0,
        12: 1, 13: 1, 14: 1, 15: 1,
    }
    layout_kind = None
    numa_layout = None
    socket_layout = None

    def __init__(self, fake=False, lscpu_output=None):
        if fake and not lscpu_output:
            self.numa_layout = self.socket_layout = self.__FAKE_LAYOUT
        else:
            self.detect_layouts(lscpu_output=lscpu_output)
        multi_numa_topology = len(set(self.numa_layout.values())) >= 2
        self.layout = self.numa_layout if multi_numa_topology else self.socket_layout
        self.layout_kind = 'NUMA' if multi_numa_topology else 'SOCKET'

    def detect_layouts(self, lscpu_output=None):
        """ Determine NUMA and sockets layout """
        stdout = self.detect_layout_lscpu(lscpu_output)
        rows = [row for row in stdout.strip().split('\n') if not row.startswith('#')]
        layouts = [[any2int(value) for value in row.split(',')][2:4] for row in rows]
        socket_layout, numa_layout = zip(*layouts)
        self.numa_layout = dict(enumerate(numa_layout))
        self.socket_layout = dict(enumerate(socket_layout))

    def detect_layout_lscpu(self, lscpu_output=None):
        """
        :param lscpu_output: <str> with output of `lscpu -p` or None
        :return: <str> output of `lscpu -p` or None
        """
        if lscpu_output:
            return lscpu_output
        stdout, return_code = self.__detect_layout_lscpu()
        if return_code != 0:
            self.detect_layouts_fallback()
            return
        if isinstance(stdout, bytes):
            if version_info[0] == 3:
                stdout = stdout.decode()
            else:
                stdout = str(stdout)
        return stdout

    def detect_layouts_fallback(self):
        """
        In case of running in container where lscpu didn't work
        """
        process = Popen(['nproc'], stdout=PIPE, stderr=PIPE)
        stdout, _ = process.communicate()
        if process.returncode == 0:
            cpu_count = int(stdout.strip())
            self.socket_layout = self.numa_layout = dict(enumerate([0] * cpu_count))

    @staticmethod
    def __detect_layout_lscpu():
        process = Popen(['lscpu', '-p'], stdout=PIPE, stderr=PIPE)
        stdout, _ = process.communicate()
        return stdout, process.returncode


if __name__ == '__main__':
    __CPU = Topology()
    print_('SOCKET', __CPU.socket_layout)
    print_('NUMA', __CPU.numa_layout)
