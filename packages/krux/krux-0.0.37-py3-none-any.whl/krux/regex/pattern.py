# -*- coding:utf-8 -*-

import re
from warnings import warn
from .exceptions import *


__all__ = ['simple_pattern_to_regex']


def simple_pattern_to_regex(pattern):
    try:
        re_pattern = re.sub(r'\{([a-zA-Z_][^/:}]*)(:[^/}]*)*\}', r'(?P<\1>[^/]*)', pattern)
        if re_pattern != pattern:
            re_pattern = re.sub(r'\.', '\.', re_pattern)
            re_pattern = '^' + re_pattern.lstrip('^')
            re_pattern = re_pattern.rstrip('$') + '$'
            return re_pattern
        else:
            return pattern
    except Exception as e:
        return pattern
