# coding=utf-8

""" Everything about console output's layout """

from prettytable import PrettyTable
from six import print_


def make_table(header, align_map=None, rows=None):
    """ Wrapper for pretty table """
    table = PrettyTable()
    table.horizontal_char = table.vertical_char = table.junction_char = ' '
    try:
        table.field_names = header
    except Exception as err:
        print_(header)
        raise err
    if align_map:
        for field, align in zip(header, align_map):
            table.align[field] = align
    if rows:
        for row in rows:
            if len(row) < len(table.field_names):
                continue
            try:
                table.add_row(row)
            except Exception as err:
                print_('fields:', table.field_names)
                print_('row:', row)
                print_('rows:', rows)
                raise err
    return table
