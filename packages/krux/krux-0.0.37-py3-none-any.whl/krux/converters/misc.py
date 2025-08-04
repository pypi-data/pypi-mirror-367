# -*- coding:utf-8 -*-

import six


__all__ = ['parse_bool']


def parse_bool(s):
    if isinstance(s, six.string_types):
        s = s.upper()
        if s in ('FALSE', 'F', 'NO', 'N', '0', '0.0', ''):
            return False
        elif s in ('TRUE', 'T', 'YES', 'Y', '1', '1.0'):
            return True
    return bool(s)
