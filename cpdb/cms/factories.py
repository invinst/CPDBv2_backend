import factory
from factory.helpers import lazy_attribute
from faker import Faker

from cms.models import FAQPage as FAQ, ReportPage as Report


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


class FAQPageFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = FAQ

    @lazy_attribute
    def fields(self):
        return {
            'question_type': 'plain_text',
            'answer_type': 'multiline_text',
            'question_value': RichTextFieldFactory(texts=[self.question]),
            'answer_value': RichTextFieldFactory(texts=self.answer)
        }

    class Params:
        question = factory.LazyFunction(lambda: fake.sentence())
        answer = factory.LazyFunction(lambda: fake.sentences())


class ReportPageFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Report

    @lazy_attribute
    def fields(self):
        return {
            'publication_type': 'string',
            'publication_value': self.publication,
            'author_type': 'string',
            'author_value': self.author,
            'title_type': 'plain_text',
            'title_value': RichTextFieldFactory(texts=[self.title]),
            'excerpt_type': 'multiline_text',
            'excerpt_value': RichTextFieldFactory(texts=self.excerpt)
        }

    class Params:
        publication = factory.LazyFunction(lambda: fake.sentence())
        author = factory.LazyFunction(lambda: fake.name())
        title = factory.LazyFunction(lambda: fake.sentence())
        excerpt = factory.LazyFunction(lambda: fake.sentences())
