from data.constants import GENDER_DICT


class BaseSerializer(object):
    def __init__(self, key=None):
        if key is not None:
            self._key = key

    def __call__(self, obj):
        return [
            self.serialize(row)
            for row in obj[self._key]
        ]

    def serialize(self, obj):
        return {
            k: v(obj)
            for k, v in self._fields.iteritems()
        }


def get(key):
    def func(obj):
        return obj[key]
    return func


def get_date(key):
    def func(obj):
        if obj[key] is None:
            return None
        return obj[key].strftime('%Y-%m-%d')
    return func


def get_gender(key):
    def func(obj):
        return GENDER_DICT.get(obj[key], None)
    return func


def literal(value):
    def func(obj):
        return value
    return func
