import factory


class LinkEntity:
    def __init__(self, **kwargs):
        for key, val in kwargs.iteritems():
            setattr(self, key, val)


class LinkEntityFactory(factory.Factory):
    class Meta:
        model = LinkEntity

    type = 'LINK'
    mutability = 'MUTABLE'
    data = factory.LazyAttribute(lambda obj: {'url': obj.url})
    length = 0
    offset = 0
    block_index = 0

    class Params:
        url = 'http://example.com'
