import random

import factory
from faker import Faker

from trr.models import TRR, ActionResponse, TRRAttachmentRequest
from data.factories import OfficerFactory

fake = Faker()


class TRRFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = TRR

    officer = factory.SubFactory(OfficerFactory)
    trr_datetime = factory.LazyFunction(lambda: fake.date_time_this_decade())
    taser = factory.LazyFunction(lambda: fake.boolean())
    firearm_used = factory.LazyFunction(lambda: fake.boolean())

    subject_race = 'White'
    subject_gender = factory.LazyFunction(lambda: random.choice(['M', 'F']))
    subject_birth_year = factory.LazyFunction(lambda: random.randint(1900, 2000))


class ActionResponseFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ActionResponse

    trr = factory.SubFactory(TRRFactory)
    person = 'Member Action'


class TRRAttachmentRequestFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = TRRAttachmentRequest

    trr = factory.SubFactory(TRRFactory)
    email = factory.LazyFunction(lambda: fake.email())
