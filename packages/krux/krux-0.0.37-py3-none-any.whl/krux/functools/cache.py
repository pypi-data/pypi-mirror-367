# -*- coding:utf-8 -*-

import six
import functools


__all__ = ['cache']


if six.PY3:
    cache = functools.lru_cache(maxsize=1024)
else:
    def cache(func):
        _cache = func.cache = {}

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return _cache[args]
            except KeyError:
                rv = func(*args, **kwargs)
                _cache[args] = rv
                return rv
        return wrapper
