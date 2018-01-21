# coding=utf-8

import os
import shutil


class Collector(object):
    """ Temporary wrapper, later collection will be fully rewritten in python """

    def __init__(self, directory, tarball, collect):
        self.directory = directory
        self.tarball = tarball
        self.__collect(collect)
        self.__archive()

    def __collect(self, collect):
        already_exists = os.path.exists(self.directory)
        if already_exists and not collect:
            return
        if already_exists:
            shutil.rmtree(self.directory)
        os.makedirs(self.directory)
        os.system('server-info-collect {0}'.format(self.directory))

    def __archive(self):
        if not self.tarball:
            return
        os.chdir(os.path.join(self.directory, '..'))
        os.system('tar cfz {0} {1} 2>/dev/null'.format(self.tarball, self.directory))
