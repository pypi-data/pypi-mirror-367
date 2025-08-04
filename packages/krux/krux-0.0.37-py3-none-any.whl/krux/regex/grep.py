# -*- coding:utf-8 -*-

import six
import re
from .pattern import simple_pattern_to_regex


__all__ = ['grep']


def grep(pattern, seq, flags=0, parse_info=False):
    """grep greps patterns from seqs.
Parameters:
    pattern: regex pattern str or compiled regex pattern or func.
    seq: seq of str or any other stuffs, etc. If pattern is not func and seq[0] is not str/unicode, seq will be converted using str() first.
    flags: 'ILMSUX' or number of re.I|re.L|re.M|re.S|re.U|re.X .
        I: ignore case;
        L: locale dependent;
        M: multi-line;
        S: dot matches all;
        U: unicode dependent;
        X: verbose.
Returns:
    A filtered list of matched str or (matched_str, groupdict). The latter applies only when the pattern has groups.
    """
    pattern = simple_pattern_to_regex(pattern)

    if isinstance(flags, six.string_types):
        true_flags = 0
        flags = flags.upper()
        for letter in flags:
            if letter in 'ILMSUX':
                true_flags += re.__dict__[letter]
    else:
        true_flags = flags

    res = []
    if isinstance(pattern, six.string_types + (type(re.compile(r'')),)):
        for item in seq:
            m = re.search(pattern, repr(item), true_flags)
            if not m:
                continue

            groupdict = m.groupdict().copy()
            groups = m.groups()
            groupdict.update(dict(zip(range(1, len(groups)+1), groups)))
            if parse_info:
                res.append((item, groupdict))
            else:
                res.append(item)
    elif callable(pattern):
        for item in seq:
            info = pattern(item)
            if info:
                if parse_info:
                    if not isinstance(info, dict):
                        res.append((item, {}))
                    else:
                        res.append((item, info))
                else:
                    res.append(item)

    return res
