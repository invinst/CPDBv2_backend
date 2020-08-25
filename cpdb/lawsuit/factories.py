import random
import pytz

import factory
from faker import Faker
from factory.django import DjangoModelFactory

from lawsuit.models import (
    Lawsuit,
    LawsuitPlaintiff,
    Payment
)


fake = Faker()


class LawsuitFactory(DjangoModelFactory):
    class Meta:
        model = Lawsuit

    case_no = factory.LazyFunction(lambda: f"{str(random.randint(1, 100))}-CV-{str(random.randint(1, 10000))}")
    incident_date = factory.LazyFunction(lambda: fake.date_time(tzinfo=pytz.utc))


class LawsuitPlaintiffFactory(DjangoModelFactory):
    class Meta:
        model = LawsuitPlaintiff

    name = factory.LazyFunction(fake.name)


class PaymentFactory(DjangoModelFactory):
    class Meta:
        model = Payment

    payee = factory.LazyFunction(fake.word)
    settlement = factory.LazyFunction(lambda: fake.pyfloat(left_digits=14, right_digits=2, positive=True))
    legal_fees = factory.LazyFunction(lambda: fake.pyfloat(left_digits=14, right_digits=2, positive=True))
    lawsuit = factory.SubFactory(LawsuitFactory)
