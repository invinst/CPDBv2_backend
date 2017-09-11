import numpy as np


def wrap(value):
    if value is [] or value is None or value is np.nan:
        return []

    if not isinstance(value, list):
        return [value]

    return value
