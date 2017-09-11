import re
import pytz
from datetime import datetime

import numpy as np
import pandas as pd
from tqdm import tqdm

from data.utils.clean_name import fix_typo_o, correct_title, remove_wrong_spacing, correct_irish_name, \
    correct_suffix_dot, correct_suffix_jr_sr, correct_initial, capitalise_generation_suffix


def ignore_null(func):
    def wrapped(value):
        if pd.isnull(value):
            return value

        return func(value)

    return wrapped


class ToBool(object):
    def __init__(self, true_set=None, false_set=None):
        self.true_set = true_set or []
        self.false_set = false_set or []

    def __call__(self, value):
        if value in self.true_set:
            return True

        if value in self.false_set:
            return False

        raise Exception('Unknown value `{}`'.format(value))


class ToNaN(object):
    def __init__(self, value_set=None):
        self.value_set = value_set or []

    def __call__(self, value):
        if value in self.value_set:
            return np.nan

        return value


class ToDateTime(object):
    def __init__(self, patterns=None, timezone='America/Chicago'):
        self.patterns = patterns or []
        self.timezone = timezone

    def __call__(self, value):
        if pd.isnull(value):
            return value

        for pattern in self.patterns:
            try:
                d = pytz.timezone(self.timezone).localize(datetime.strptime(value, pattern))

                if d > datetime.now(pytz.timezone(self.timezone)):
                    d = d.replace(year=d.year - 100)

                return d
            except ValueError:
                pass

        raise Exception('Date format {} is not supported'.format(value))


class ToDate(object):
    def __init__(self, patterns=None, timezone='America/Chicago'):
        self.patterns = patterns or []
        self.timezone = timezone

    def __call__(self, value, timezone='America/Chicago'):
        if pd.isnull(value):
            return value

        return ToDateTime(self.patterns, timezone)(value).date()


class ZFill(object):
    def __init__(self, padding=0):
        self.padding = padding

    def __call__(self, value):
        if pd.isnull(value):
            return value

        return str(int(float(value))).zfill(self.padding)


class Just(object):
    def __init__(self, value):
        self.value = value

    def __call__(self, _):
        return self.value


def strip(value):
    if pd.isnull(value):
        return value

    return str.strip(str(value))


def to_int(value):
    if pd.isnull(value):
        return value

    return int(float(value))


capitalise_generation_suffix = ignore_null(capitalise_generation_suffix)


def clean_name(name):
    new_name = fix_typo_o(name)
    new_name = new_name.title()
    new_name = correct_title(new_name)
    new_name = remove_wrong_spacing(new_name)
    new_name = capitalise_generation_suffix(new_name)
    new_name = correct_irish_name(new_name)
    new_name = correct_suffix_dot(new_name)
    new_name = correct_suffix_jr_sr(new_name)
    new_name = correct_initial(new_name)

    return new_name


def titleize(st):
    if pd.isnull(st):
        return st

    return re.sub(r"[A-Za-z]+('[A-Za-z]+)?", lambda mo: mo.group(0)[0].upper() + mo.group(0)[1:].lower(), st)


class DataCleaner(object):
    def __init__(self, schema):
        self.schema = schema or {}

    def perform(self, df):
        for key, cleans in tqdm(self.schema.items()):
            for clean in cleans:
                df[key] = df.apply(lambda x: clean(x.get(key, np.NaN)), axis=1)

        return df
