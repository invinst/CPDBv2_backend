import random
import pytz

import factory
from faker import Faker
from factory.django import DjangoModelFactory

from lawsuit.models import (
    Lawsuit,
    LawsuitPlaintiff,
    LawsuitInteraction,
    LawsuitService,
    LawsuitMisconduct,
    LawsuitViolence,
    LawsuitOutcome,
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


class LawsuitInteractionFactory(DjangoModelFactory):
    class Meta:
        model = LawsuitInteraction

    name = factory.LazyFunction(fake.word)


class LawsuitServiceFactory(DjangoModelFactory):
    class Meta:
        model = LawsuitService

    name = factory.LazyFunction(fake.word)


class LawsuitMisconductFactory(DjangoModelFactory):
    class Meta:
        model = LawsuitMisconduct

    name = factory.LazyFunction(fake.word)


class LawsuitViolenceFactory(DjangoModelFactory):
    class Meta:
        model = LawsuitViolence

    name = factory.LazyFunction(fake.word)


class LawsuitOutcomeFactory(DjangoModelFactory):
    class Meta:
        model = LawsuitOutcome

    name = factory.LazyFunction(fake.word)


class PaymentFactory(DjangoModelFactory):
    class Meta:
        model = Payment

    payee = factory.LazyFunction(fake.word)
    settlement = factory.LazyFunction(lambda: fake.pyfloat(left_digits=14, right_digits=2, positive=True))
    legal_fees = factory.LazyFunction(lambda: fake.pyfloat(left_digits=14, right_digits=2, positive=True))
    lawsuit = factory.SubFactory(LawsuitFactory)
