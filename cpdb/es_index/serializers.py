from data.constants import GENDER_DICT, FINDINGS_DICT


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


def get(key, default_value=None):
    def func(obj):
        value = obj.get(key, None)
        return value if value is not None else default_value
    return func


def get_date(key):
    def func(obj):
        if obj[key] is None:
            return None
        return obj[key].strftime('%Y-%m-%d')
    return func


def get_gender(key, default_value=None):
    def func(obj):
        return GENDER_DICT.get(obj[key], default_value)
    return func


def literal(value):
    def func(obj):
        return value
    return func


def get_age_range(ranges, key, default_value=None):
    len_ranges = len(ranges)

    def func(obj):
        age = obj[key]
        if age is None:
            return default_value

        for ind, val in enumerate(ranges):
            if age < val:
                if ind == 0:
                    return '<%d' % val
                else:
                    return '%d-%d' % (ranges[ind-1], val)
            elif ind == len_ranges - 1:
                return '%d+' % val
    return func


def get_finding(key, default_value=None):
    def func(obj):
        return FINDINGS_DICT.get(obj[key], default_value)
    return func


def get_point(key, default_value=None):
    def func(obj):
        if obj.get(key, None) is None:
            return default_value
        return {'lon': obj[key].x, 'lat': obj[key].y}
    return func
