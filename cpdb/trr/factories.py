import random
import pytz

import factory
from faker import Faker

from trr.models import TRR, ActionResponse, TRRAttachmentRequest
from data.factories import OfficerFactory, PoliceUnitFactory

fake = Faker()


class TRRFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = TRR

    officer = factory.SubFactory(OfficerFactory)
    trr_datetime = factory.LazyFunction(lambda: fake.date_time_this_decade(tzinfo=pytz.utc))
    taser = factory.LazyFunction(lambda: fake.boolean())
    firearm_used = factory.LazyFunction(lambda: fake.boolean())

    subject_race = 'White'
    subject_gender = factory.LazyFunction(lambda: random.choice(['M', 'F']))
    subject_birth_year = factory.LazyFunction(lambda: random.randint(1900, 2000))
    officer_unit = factory.SubFactory(PoliceUnitFactory)
    officer_unit_detail = factory.SubFactory(PoliceUnitFactory)


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
