from itertools import zip_longest

START = object()  # just using as a unique symbol


def pair_looper(iterator):
    '''
    Loop through iterator yielding items in adjacent pairs
    '''
    left = START
    for item in iterator:
        if left is not START:
            yield (left, item)
        left = item


def first_last_iterator(iterable):
    lst = list(iterable)
    length = len(lst)
    for index, item in enumerate(lst):
        yield index == 0, index == (length - 1), item


def group_by(iterable, n, fill=None):
    args = [iter(iterable)] * n
    return list(''.join(s) for s in zip_longest(*args, fillvalue=fill))
