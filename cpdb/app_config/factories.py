from functools import partial

import factory
from faker import Faker
from faker.providers import color
from factory.django import DjangoModelFactory

from app_config.models import VisualTokenColor


fake = Faker()
fake.add_provider(color)


class VisualTokenColorFactory(DjangoModelFactory):
    class Meta:
        model = VisualTokenColor

    color = factory.LazyFunction(partial(fake.color, hue='red'))
    text_color = factory.LazyFunction(partial(fake.color, hue='red'))
    lower_range = factory.LazyFunction(partial(fake.pyint, min_value=0, max_value=100))
    upper_range = factory.LazyFunction(partial(fake.pyint, min_value=0, max_value=100))
