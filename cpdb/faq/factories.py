import json

from django.contrib.contenttypes.models import ContentType

from factory.django import DjangoModelFactory
from factory import LazyFunction
from faker import Faker

from faq.models import FAQ, FAQPage, FAQsPage

fake = Faker()


class FAQFactory(DjangoModelFactory):
    class Meta:
        model = FAQ

    title = LazyFunction(fake.sentence)
    body = json.dumps([{
        'type': 'paragraph',
        'value': fake.text()
        }])


class FAQPageFactory(DjangoModelFactory):
    class Meta:
        model = FAQPage

    content_type = ContentType.objects.get_for_model(FAQPage)
    title = LazyFunction(fake.sentence)
    body = json.dumps([{
        'type': 'paragraph',
        'value': fake.text()
        }])


class FAQsPageFactory(DjangoModelFactory):
    class Meta:
        model = FAQsPage

    content_type = ContentType.objects.get_for_model(FAQsPage)
    title = 'FAQ'
    slug = 'faq'
