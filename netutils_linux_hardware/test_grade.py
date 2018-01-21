#!/usr/bin/env python
# coding=utf-8

""" Tests of grade in scale of 1..10 """

from unittest import TestCase, main

from six import iteritems

from netutils_linux_hardware.grade import Grade
from netutils_linux_hardware.rate_math import any2int


class GradeTest(TestCase):
    def test_grade_int(self):
        self.longMessage = True
        self.assertEqual(Grade.int(2000, 2000, 4000), 1)
        self.assertEqual(Grade.int(1000, 2000, 4000), 1)
        self.assertEqual(Grade.int(-1000, 2000, 4000), 1)
        self.assertEqual(Grade.int(2200, 2000, 4000), 2)
        self.assertEqual(Grade.int(3000, 2000, 4000), 6)
        self.assertEqual(Grade.int(3999, 2000, 4000), 10)
        self.assertEqual(Grade.int(4000, 2000, 4000), 10)
        self.assertEqual(Grade.int(5000, 2000, 4000), 10)
        self.assertEqual(Grade.int(5000, 2000, 4000, 15), 15)
        self.assertEqual(Grade.int(4000, 2000, 4000, 15), 15)

    def test_grade_str(self):
        bad = ['Realtek', 'Dlink']
        good = ['Intel', 'Melanox']
        expected = {
            'Melanox': 10,
            'Intel': 10,
            'Broadcom': 2,
            'Dlink': 1,
            'Realtek': 1,
        }
        for k, value in iteritems(expected):
            self.assertEqual(Grade.str(k, good, bad), value)

    def test_grade_fact(self):
        self.assertEqual(Grade.fact(None, True), 1)
        self.assertEqual(Grade.fact(None), 10)
        self.assertEqual(Grade.fact('Anything', True), 10)
        self.assertEqual(Grade.fact('Anything'), 1)
        self.assertEqual(Grade.fact(15, True), 10)
        self.assertEqual(Grade.fact(15), 1)
        self.assertEqual(Grade.fact({'x': 'y'}, True), 10)
        self.assertEqual(Grade.fact({}, True), 10)

    def test_any2int(self):
        self.assertEqual(any2int(None), 0)
        self.assertEqual(any2int(23), 23)
        self.assertEqual(any2int(23.1), 23)
        self.assertEqual(any2int('23'), 23)
        self.assertEqual(any2int('23K'), 23)
        self.assertEqual(any2int('23 K'), 23)
        self.assertEqual(any2int(' '), 0)


if __name__ == '__main__':
    main()
