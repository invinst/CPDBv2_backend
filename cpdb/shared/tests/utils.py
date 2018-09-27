from mock import Mock
from robber import expect


def create_object(dict_object):
    return Mock(spec=dict_object.keys(), **dict_object)


def validate_object(obj, data):
    for key, value in data.iteritems():
        expect(getattr(obj, key, None)).to.eq(value)
