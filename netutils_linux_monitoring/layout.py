# coding=utf-8

""" Everything about console output's layout """

from prettytable import PrettyTable
from six import print_


def make_table(header, align_map=None, rows=None):
    """ Wrapper for pretty table """
    t = PrettyTable()
    t.horizontal_char = t.vertical_char = t.junction_char = ' '
    t.field_names = header
    if align_map:
        for field, align in zip(header, align_map):
            t.align[field] = align
    if rows:
        for row in rows:
            if len(row) < len(t.field_names):
                continue
            try:
                t.add_row(row)
            except Exception as err:
                print_('fields:', t.field_names)
                print_('row:', row)
                print_('rows:', rows)
                raise err
    return t
