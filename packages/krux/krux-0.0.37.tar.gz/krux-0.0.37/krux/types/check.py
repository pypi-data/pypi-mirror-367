# -*- coding:utf-8 -*-

import six
import numpy as np
from collections import deque

__all__ = ['is_integer', 'is_float', 'is_seq']



def is_integer(value):
    return isinstance(value, six.integer_types + (np.integer,))


def is_float(value):
    return isinstance(value, (float, np.floating))


def is_seq(value):
    if isinstance(value, (list, tuple, deque)):
        return True
    elif isinstance(value, np.ndarray):
        return value.ndim == 1

    return False
