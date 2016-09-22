import json

from django.contrib.contenttypes.models import ContentType

from factory.django import DjangoModelFactory
from factory import LazyFunction
from faker import Faker

from faq.models import FAQPage, FAQsPage

fake = Faker()


class FAQPageFactory(DjangoModelFactory):
    class Meta:
        model = FAQPage

    content_type = LazyFunction(lambda: ContentType.objects.get_for_model(FAQPage))
    title = LazyFunction(fake.sentence)
    body = json.dumps([{
        'type': 'paragraph',
        'value': fake.text()
        }])


class FAQsPageFactory(DjangoModelFactory):
    class Meta:
        model = FAQsPage

    content_type = LazyFunction(lambda: ContentType.objects.get_for_model(FAQsPage))
    title = 'FAQ'
    slug = 'faq'
