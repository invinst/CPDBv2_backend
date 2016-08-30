import json

from factory.django import DjangoModelFactory
from factory import LazyFunction
from faker import Faker

from faq.models import FAQ

fake = Faker()


class FAQFactory(DjangoModelFactory):
    class Meta:
        model = FAQ

    title = LazyFunction(fake.sentence)
    body = json.dumps([{
        'type': 'paragraph',
        'value': fake.text()
        }])
