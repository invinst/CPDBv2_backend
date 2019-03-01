import random
import factory

from faker import Faker

from data.factories import AttachmentFileFactory
from .models import SearchTracking, AttachmentTracking
from .constants import QUERY_TYPES

fake = Faker()


class SearchTrackingFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = SearchTracking

    query = factory.LazyFunction(lambda: fake.name())
    results = factory.LazyAttribute(lambda: random.randint(1, 10))
    usages = factory.LazyAttribute(lambda: random.randint(1, 10))
    query_type = factory.LazyFunction(lambda: random.choice(QUERY_TYPES)[0])


class AttachmentTrackingFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = AttachmentTracking

    attachment_file = factory.SubFactory(AttachmentFileFactory)
    accessed_from_page = factory.LazyFunction(lambda: fake.word())
    app = factory.LazyFunction(lambda: fake.word())
