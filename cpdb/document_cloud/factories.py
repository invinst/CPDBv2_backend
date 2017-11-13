import factory
from faker import Faker

from document_cloud.constants import DOCUMENT_TYPES
from document_cloud.models import DocumentCloudSearchQuery

fake = Faker()


class DocumentCloudSearchQueryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = DocumentCloudSearchQuery
    type = factory.Sequence(lambda n: fake.random_element(x[0] for x in DOCUMENT_TYPES))
    query = factory.Sequence(lambda n: str(n))
