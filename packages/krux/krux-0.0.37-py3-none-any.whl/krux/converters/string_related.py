# -*- coding:utf-8 -*-

import six
import sys
import re
from hashlib import md5

__all__ = ['str2list', 'dict2str', 'str2md5', 'Str2Obj', 'str2obj']


def str2list(s, pattern=',|;|:|#|&|\||\s+'):
    l = re.split(pattern, s)
    if len(l) == 1 and l[0] == '':
        return []
    else:
        return l


def dict2str(d, fmt='{}={}', delimiter='&', sort=True):
    keys = sorted(d.keys()) if sort else d.keys()
    tokens = [fmt.format(k, d[k]) for k in keys]
    return delimiter.join(tokens)


def str2md5(s, length=None, upper=False):
    if (six.PY2 and isinstance(s, unicode)) or (six.PY3 and isinstance(s, str)):
        s = s.encode('utf-8')
    m = md5()
    m.update(s)
    result = m.hexdigest()
    if length is not None:
        result = result[:length]
    if upper:
        result = result.upper()
    return result


class Str2Obj(object):
    """Str2Obj converts str to actual object.
    inspired by django's ContentTyper
    """
    def __init__(self):
        self.cache = {}
        self.registered = {}

    def register(self, name, func):
        """
        register a generator func.
        :param name: generator name
        :param func: generator func
        :return: info dict.
        """
        self.registered[name] = func

    def deregister(self, name=None):
        if name is None:
            self.registered.clear()
        else:
            self.registered.pop(name, None)

    def clear_cache(self, name=None):
        if name is None:
            self.cache.clear()
        else:
            self.cache.pop(name, None)

    def _return_or_raise(self, value, msg=None):
        if isinstance(value, six.class_types) and issubclass(value, Exception):
            raise value(msg)
        elif isinstance(value, Exception):
            raise value
        else:
            return value

    def __call__(self, s, entrance=None, default=ValueError, cache=True):
        """

        :param s: the string to be converted.
            which can be like 'a', 'a.b.c', 'f()', 'f("arg", kw="v", ...)';
            if s is not a string, it will be returned as it is.
        :param entrance: if provided, retrieve the object from this dict.
        :param default: a default value or an exception class/object to be raised. default: ValueError;
        :param cache: whether to use cache.
        :return: converted object.
        """
        if not isinstance(s, six.string_types):
            return s

        m = re.match(r'^(?P<name>.*?)(\((?P<args>.*)\))?$', s)
        name = m.group('name')
        if name in self.registered:
            obj = self.registered[name]
        else:
            if entrance is None:
                import importlib

                if name in self.cache:
                    obj = self.cache[name]
                else:
                    tokens = name.split('.')
                    try:
                        if len(tokens) > 1:
                            obj = importlib.import_module(tokens[0])
                            for i in range(1, len(tokens)):
                                try:
                                    obj = getattr(obj, tokens[i])
                                except AttributeError:
                                    obj = importlib.import_module('.'.join(tokens[:i+1]))
                        else:
                            scope = sys.modules['__main__'].__dict__
                            obj = scope[tokens[0]]
                        if cache:
                            self.cache[s] = obj
                    except Exception as e:
                        # self.cache[s] = Null
                        return self._return_or_raise(default, repr(e))

            else:
                # not using cache
                tokens = name.split('.')
                obj = entrance
                try:
                    for tk in tokens:
                        try:
                            obj = obj[tk]
                        except TypeError:
                            try:
                                obj = getattr(obj, tk)
                            except AttributeError:
                                raise ValueError(u"Cannot get %s in %s" % (name, entrance))
                except Exception as e:
                    return self._return_or_raise(default, msg=repr(e))

        raw_args = m.group('args')
        if raw_args is None:
            return obj
        else:
            try:
                res = eval('obj({})'.format(raw_args))
                return res
            except Exception as e:
                return self._return_or_raise(default, repr(e))


str2obj = Str2Obj()
