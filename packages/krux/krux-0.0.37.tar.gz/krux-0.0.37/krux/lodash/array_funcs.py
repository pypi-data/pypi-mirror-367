__all__ = ['batched', 'batch']


def batched(iterable, n):
    """
    Author: Eric Cotner
    Source: https://discuss.python.org/t/add-batching-function-to-itertools-module/19357
    Conforms to Python 3.12 itertools.batched
    Batches an iterable into lists of given maximum size, yielding them one by one.
    """
    batch = []
    for element in iterable:
        batch.append(element)
        if len(batch) >= n:
            yield batch
            batch = []
    if len(batch) > 0:
        yield batch


def batch(array, size=1):
    """
    Creates an array of elements split into groups the length of size. If array can't be split evenly, the final chunk will be the remaining elements.
    Conform to lodash.batch
    """
    return batched(array, size)
