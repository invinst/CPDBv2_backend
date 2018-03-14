from factory import LazyFunction, SubFactory
from factory.django import DjangoModelFactory
from faker import Faker

from data.factories import OfficerFactory
from trr.models import TRR

fake = Faker()


class TRRFactory(DjangoModelFactory):
    class Meta:
        model = TRR

    trr_datetime = LazyFunction(lambda: fake.past_datetime())
    officer = SubFactory(OfficerFactory)
