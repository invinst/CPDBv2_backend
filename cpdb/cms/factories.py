import factory
from factory.helpers import lazy_attribute
from faker import Faker


fake = Faker()


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


class BlockFactory(factory.Factory):
    class Meta:
        model = dict

    data = {}
    depth = 0
    entityRanges = []
    inlineStyleRanges = []
    key = '411c9'
    text = factory.LazyFunction(lambda: fake.sentence())
    type = 'unstyled'


class RichTextFieldFactory(factory.Factory):
    class Meta:
        model = dict

    entityMap = {}

    @lazy_attribute
    def blocks(self):
        return [BlockFactory(text=text) for text in self.texts]

    class Params:
        texts = factory.LazyFunction(lambda: fake.sentences())
