# -*- coding:utf-8 -*-

import six
import unittest

import os
import sys
import re
import datetime

from krux.converters import *


class TestStr2Obj(unittest.TestCase):
    def test_import(self):
        for s, obj in [
            ('sys.path', sys.path),
            ('datetime.datetime.now', datetime.datetime.now),

        ]:
            self.assertEqual(str2obj(s), obj)

    def test_raise(self):
        with self.assertRaises(ValueError):
            str2obj('not_a_lib.def.g')

        with self.assertRaises(RuntimeError):
            str2obj('not_a_lib.def.g', default=RuntimeError)

    def test_default(self):
        self.assertEqual(str2obj('not_a_lib.def.g', default='foo'), 'foo')

    def test_dict(self):
        class C(object):
            x = 5

        d = {
            "a": {
                "b": 1
            },
            "c": C()
        }

        default = 99
        for s, val in [
            ('a.b', 1),
            ('c.x', 5),
            ('c.y', default),
            ('d', default),
            ('a.b.c', default),
        ]:
            self.assertEqual(str2obj(s, entrance=d, default=default), val)

    def test_func(self):
        self.assertEqual(str2obj('operator.add(3, 5)'), 8)


if __name__ == '__main__':
    unittest.main()