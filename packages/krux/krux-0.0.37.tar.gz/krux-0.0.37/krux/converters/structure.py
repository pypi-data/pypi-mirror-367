# -*- coding:utf-8 -*-


__all__ = ['list2dict', 'dict2list']


def list2dict(l):
    if not l:
        return {}

    keys = l[0].keys()
    d = {}
    for k in keys:
        d[k] = [item[k] for item in l]

    return d


def dict2list(d):
    if not d:
        return []

    keys = d.keys()
    zipped = zip(*d.values())
    return [dict(zip(keys, tup)) for tup in zipped]