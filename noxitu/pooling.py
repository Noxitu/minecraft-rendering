import numpy as np

def _pool(X, op):
    a = slice(1, None)
    b = slice(None, -1)
    c = slice(None, None)

    q = [(a, b), (c, c), (b, a)]

    res = X.copy()

    for y1, y2 in q:
        for x1, x2 in q:
            op(res[y1, x1], X[y2, x2], out=res[y1, x1])

    return res


def min_pool(X):
    return _pool(X, np.minimum)


def max_pool(X):
    return _pool(X, np.maximum)
