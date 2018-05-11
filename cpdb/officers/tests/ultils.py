from robber import expect


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


def create_object(props):
    obj = Object()
    for key, value in props.iteritems():
        setattr(obj, key, value)

    return obj
