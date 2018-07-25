from robber import expect
from mock import Mock


def validate_object(obj, data):
    for key, value in data.iteritems():
        expect(getattr(obj, key, None)).to.eq(value)


class Object(object):
    def __str__(self):
        props = [
            {prop: getattr(self, prop)}
            for prop in dir(self) if not prop.startswith('__') and not callable(getattr(self, prop))
        ]
        return str(props)

    __repr__ = __str__


def create_object(dict_object):
    return Mock(spec=dict_object.keys(), **dict_object)
