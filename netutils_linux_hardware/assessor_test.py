#!/usr/bin/env python

from unittest import TestCase, main
from six import iteritems
from netutils_linux_hardware import Assessor


class AssessorTest(TestCase):

    def test_grade_int(self):
        self.longMessage = True
        assessor = Assessor(None)
        self.assertEqual(assessor.grade_int(2000, 2000, 4000), 1)
        self.assertEqual(assessor.grade_int(1000, 2000, 4000), 1)
        self.assertEqual(assessor.grade_int(-1000, 2000, 4000), 1)
        self.assertEqual(assessor.grade_int(2200, 2000, 4000), 2)
        self.assertEqual(assessor.grade_int(3000, 2000, 4000), 6)
        self.assertEqual(assessor.grade_int(3999, 2000, 4000), 10)
        self.assertEqual(assessor.grade_int(4000, 2000, 4000), 10)
        self.assertEqual(assessor.grade_int(5000, 2000, 4000), 10)
        self.assertEqual(assessor.grade_int(5000, 2000, 4000, 15), 15)
        self.assertEqual(assessor.grade_int(4000, 2000, 4000, 15), 15)

    def test_grade_str(self):
        bad = ["Realtek", "Dlink"]
        good = ["Intel", "Melanox"]
        expected = {
            "Melanox": 10,
            "Intel": 10,
            "Broadcom": 2,
            "Dlink": 1,
            "Realtek": 1,
        }
        for k, v in iteritems(expected):
            self.assertEqual(Assessor.grade_str(k, good, bad), v)

    def test_grade_fact(self):
        self.assertEqual(Assessor.grade_fact(None, True), 1)
        self.assertEqual(Assessor.grade_fact(None, False), 10)
        self.assertEqual(Assessor.grade_fact("Anything", True), 10)
        self.assertEqual(Assessor.grade_fact("Anything", False), 1)
        self.assertEqual(Assessor.grade_fact(15, True), 10)
        self.assertEqual(Assessor.grade_fact(15, False), 1)
        self.assertEqual(Assessor.grade_fact({'x': 'y'}, True), 10)
        self.assertEqual(Assessor.grade_fact({}, True), 10)

    def test_any2int(self):
        assessor = Assessor(None)
        self.assertEqual(assessor.any2int(None), 0)
        self.assertEqual(assessor.any2int(23), 23)
        self.assertEqual(assessor.any2int(23.1), 23)
        self.assertEqual(assessor.any2int("23"), 23)
        self.assertEqual(assessor.any2int("23K"), 23)
        self.assertEqual(assessor.any2int("23 K"), 23)
        self.assertEqual(assessor.any2int(" "), 0)

    def test_grade_list(self):
        assessor = Assessor(None)
        self.assertEqual(assessor.grade_list([], 1, 4), 1)
        self.assertEqual(assessor.grade_list([1], 1, 4), 1)
        self.assertEqual(assessor.grade_list([1, 2, 3, 4], 1, 4), 10)


if __name__ == '__main__':
    main()
