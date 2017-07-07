import random
import factory

from faker import Faker

from .models import SearchTracking
from .constants import QUERY_TYPES

fake = Faker()


class SearchTrackingFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = SearchTracking

    query = factory.LazyFunction(lambda: fake.name())
    results = factory.LazyAttribute(lambda: random.randint(1, 10))
    usages = factory.LazyAttribute(lambda: random.randint(1, 10))
    query_type = factory.LazyFunction(lambda: random.choice(QUERY_TYPES)[0])
