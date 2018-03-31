import factory
from faker import Faker

from trr.models import TRR
from data.factories import OfficerFactory

fake = Faker()


class TRRFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = TRR

    officer = factory.SubFactory(OfficerFactory)
    trr_datetime = factory.LazyFunction(lambda: fake.date_time_this_decade())
    taser = factory.LazyFunction(lambda: fake.boolean())
    firearm_used = factory.LazyFunction(lambda: fake.boolean())
