import random

import factory
from faker import Faker

from document_cloud.constants import DOCUMENT_TYPES
from document_cloud.models import DocumentCloudSearchQuery, DocumentCrawler

fake = Faker()


class DocumentCloudSearchQueryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = DocumentCloudSearchQuery

    type = factory.Sequence(lambda n: fake.random_element([x[0] for x in DOCUMENT_TYPES]))
    query = factory.Sequence(lambda n: str(n))


class DocumentCrawlerFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = DocumentCrawler

    source_type = factory.LazyFunction(lambda: fake.word())
    num_documents = factory.LazyFunction(lambda: str(random.randint(0, 100)))
    num_new_documents = factory.LazyFunction(lambda: str(random.randint(0, 100)))
    num_updated_documents = factory.LazyFunction(lambda: str(random.randint(0, 100)))
