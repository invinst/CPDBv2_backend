import json

from django.contrib.contenttypes.models import ContentType

from factory.django import DjangoModelFactory
from factory import LazyFunction
from faker import Faker

from faq.models import FAQPage

fake = Faker()


class FAQPageFactory(DjangoModelFactory):
    class Meta:
        model = 'faq.FAQPage'

    content_type = ContentType.objects.get_for_model(FAQPage)
    title = LazyFunction(fake.sentence)
    body = json.dumps([{
        'type': 'paragraph',
        'value': fake.text()
        }])
