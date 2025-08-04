__all__ = ['none_min', 'none_max', 'json_safe']

from datetime import date


def none_min(a, b):
    if a is None:
        return b
    elif b is None:
        return a
    return min(a, b)


def none_max(a, b):
    if a is None:
        return b
    elif b is None:
        return a
    return max(a, b)


def json_safe(data, time_format='%Y-%m-%d %H:%M:%S'):
    import numpy as np

    if isinstance(data, dict):
        return {k: json_safe(v, time_format=time_format) for k, v in data.items()}
    elif isinstance(data, (tuple, list, np.ndarray)):
        return [json_safe(v, time_format=time_format) for v in data]
    else:
        try:
            if isinstance(data, date):
                return data.strftime(time_format)
            elif np.isscalar(data):
                if not np.isfinite(data):
                    return None
                if isinstance(data, np.floating):
                    return float(data)
                if isinstance(data, np.integer):
                    return int(data)
                return data
        except Exception as e:
            pass

        return data

