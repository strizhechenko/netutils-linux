# coding=utf-8


class Folding(object):
    NO = 0
    DEVICE = 1
    SUBSYSTEM = 2
    SERVER = 3

    def __init__(self, args):
        self.args = args

    def fold(self, data, level):
        """ Схлапывает значения в дикте до среднего арифметического """
        if not data:
            return 1
        if self.args.folding < level:
            return data
        result = sum(data.values()) / len(data.keys())
        return result if level < Folding.SERVER else {'server': result}
