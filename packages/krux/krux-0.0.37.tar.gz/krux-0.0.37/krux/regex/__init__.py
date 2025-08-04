# -*- coding:utf-8 -*-

import six
import re


__all__ = ['simple_pattern_to_regex', 'get_simple_pattern_fields', 'grep']


def simple_pattern_to_regex(pattern, mode=None, sep_chars=None, keep_dots=False, strict=False):
    """simple_pattern_to_regex converts a simple pattern into a regex pattern.
    :param pattern: a curly-bracketed pattern, like str's named format pattern, e.g. '{dataset}/{varname}.csv'
    :param mode: choices: None (default); 'path';
    :param sep_chars: chars that is always considered as delimiters, e.g., "/" in file path. Default: None,
    :param keep_dots: if False, "." is converted to "\.". Default: False.
    :param strict: if True, add "^" and "$" to the begining and end of the pattern. Default: False
    :return: regex pattern, e.g. r"(?P<dataset>[^/]*)/(?P<varname>[^/]*)\.nc"
    """

    res_list = []
    group_name_list = []
    state = 'n'
    group_name_state = False
    for i, c in enumerate(pattern):
        if state == 'n':
            if c == '{':
                state = 'g'
                group_name_state = True
            elif c in '}':
                raise ValueError(u"Invalid pattern {} at char {}".format(pattern, i))
            else:
                if c == '.' and not keep_dots:
                    res_list.append(r'\.')
                else:
                    res_list.append(c)
        elif state == 'g':
            if c == '}':
                valid_char_pattern = r'[^{}]'.format(sep_chars) if sep_chars else r'.'
                if len(group_name_list) == 0:
                    res_list.append(r'({}*)'.format(valid_char_pattern))
                else:
                    group_name = ''.join(group_name_list)
                    if re.match(r'^\d.*', group_name):
                        raise ValueError(u"Invalid group name {}".format(group_name))

                    if mode == 'path':
                        # TODO: consider sep_chars
                        if re.match(r'^[A-Z0-9_]*$', group_name):
                            valid_char_pattern = r'.'
                        else:
                            valid_char_pattern = r'[^/]'
                    res_list.append(r'(?P<{}>{}*)'.format(group_name, valid_char_pattern))
                state = 'n'
                group_name_state = False
                group_name_list = []
            elif c == ':':
                group_name_state = False
            else:
                if group_name_state:
                    if re.match(r'[A-Za-z0-9_]', c):
                        group_name_list.append(c)
                    else:
                        raise ValueError(u"Invalid pattern {} at char {}".format(pattern, i))
                else:
                    pass

    result = ''.join(res_list)
    if strict:
        if not result.startswith('^'):
            result = '^' + result
        if not result.endswith('$'):
            result = result + '$'

    return result


def get_simple_pattern_fields(pattern):
    return re.findall(r'\{([A-Za-z_][A-Za-z0-9_]*)[^}]*\}', pattern)


def grep(pattern, seq, flags=0, parse_info=False):
    """grep greps patterns from seqs.
Parameters:
    pattern: a regex pattern (str or compiled), a simple pattern, or a function-like object that returns True/False or info dict.
    seq: seq of str or any other stuffs, etc. If pattern is not func and seq[0] is not string type, seq will be converted using repr() first.
        items in seq can also be 2-tuple: (object-itself, string-representation), pattern is applied on the latter.
    flags: 'ILMSUX' or number of re.I|re.L|re.M|re.S|re.U|re.X .
        I: ignore case;
        L: locale dependent;
        M: multi-line;
        S: dot matches all;
        U: unicode dependent;
        X: verbose.
    parse_info: whether to return parsed info (e.g., group info of regex, or the result of func-like pattern)
Returns:
    A filtered list of matched str or (matched_str, groupdict). The latter applies only when the pattern has groups.
    """
    if isinstance(pattern, six.string_types) and '(?P<' not in pattern:
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
            if isinstance(item, (tuple, list)) and len(item) == 2:
                object, grep_target = item
            else:
                object = item
                grep_target = item if isinstance(item, six.string_types) else repr(item)
            m = re.search(pattern, grep_target, true_flags)
            if not m:
                continue

            info = m.groupdict().copy()
            groups = m.groups()
            info.update(dict(zip(range(1, len(groups)+1), groups)))
            if parse_info:
                res.append((object, info))
            else:
                res.append(object)
    elif callable(pattern):
        for item in seq:
            if isinstance(item, tuple) and len(item) == 2:
                object, grep_target = item
            else:
                object = item
                grep_target = item if isinstance(item, six.string_types) else repr(item)

            info = pattern(grep_target)
            if info:
                if parse_info:
                    if not isinstance(info, dict):
                        res.append((object, {}))
                    else:
                        res.append((object, info))
                else:
                    res.append(object)

    return res
