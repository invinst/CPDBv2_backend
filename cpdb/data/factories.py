import random

from django.contrib.gis.geos import MultiPolygon, Polygon, MultiLineString, LineString

import factory
from factory.fuzzy import FuzzyInteger
from faker import Faker

from data.models import (
    Area, Investigator, LineArea, Officer, OfficerBadgeNumber, PoliceUnit, Allegation, OfficerAllegation,
    Complainant, OfficerHistory, AllegationCategory, Involvement, AttachmentFile, AttachmentRequest, Victim,
    PoliceWitness, InvestigatorAllegation)
from data.constants import ACTIVE_CHOICES

fake = Faker()


class AreaFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Area

    name = factory.LazyFunction(lambda: fake.word())
    area_type = 'school-grounds'
    polygon = factory.LazyFunction(lambda: MultiPolygon(Polygon((
        (87.940101, 42.023135),
        (87.523661, 42.023135),
        (87.523661, 41.644286),
        (87.940101, 41.644286),
        (87.940101, 42.023135)))))


class LineAreaFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = LineArea

    name = factory.LazyFunction(lambda: fake.word())
    linearea_type = 'passageway'
    geom = factory.LazyFunction(lambda: MultiLineString(
        LineString(
            (-87.6543545842184386, 41.7741537537218477),
            (-87.6543453548284504, 41.7738192794681069)
        )
    ))


class InvestigatorFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Investigator

    first_name = factory.LazyFunction(lambda: fake.name())
    last_name = factory.LazyFunction(lambda: fake.name())


class OfficerFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Officer

    first_name = factory.LazyFunction(lambda: fake.first_name())
    last_name = factory.LazyFunction(lambda: fake.last_name())
    gender = factory.LazyFunction(lambda: random.choice(['M', 'F']))
    race = 'White'
    appointed_date = factory.LazyFunction(lambda: fake.date_time().date())
    rank = factory.LazyFunction(lambda: fake.word())
    birth_year = factory.LazyFunction(lambda: random.randint(1900, 2000))
    active = factory.LazyFunction(lambda: random.choice(ACTIVE_CHOICES)[0])
    tags = factory.LazyFunction(lambda: fake.pylist(2, False, str))


class AllegationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Allegation

    crid = factory.LazyFunction(lambda: random.randint(100000, 999999))


class InvestigatorAllegationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = InvestigatorAllegation

    investigator = factory.SubFactory(InvestigatorFactory)
    allegation = factory.SubFactory(AllegationFactory)


class OfficerAllegationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = OfficerAllegation

    allegation = factory.SubFactory(AllegationFactory)
    officer = factory.SubFactory(OfficerFactory)
    start_date = factory.LazyFunction(lambda: fake.date())


class OfficerBadgeNumberFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = OfficerBadgeNumber

    officer = factory.SubFactory(OfficerFactory)
    star = factory.LazyFunction(lambda: str(random.randint(10000, 99999)))
    current = factory.LazyFunction(lambda: fake.boolean())


class PoliceUnitFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = PoliceUnit

    unit_name = factory.LazyFunction(lambda: fake.numerify(text="###"))
    description = factory.LazyFunction(lambda: fake.text(25))


class ComplainantFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Complainant

    allegation = factory.SubFactory(AllegationFactory)
    gender = factory.LazyFunction(lambda: random.choice(['M', 'F']))
    race = 'Black'
    age = FuzzyInteger(18, 60)


class AllegationCategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = AllegationCategory


class OfficerHistoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = OfficerHistory

    officer = factory.SubFactory(OfficerFactory)
    unit = factory.SubFactory(PoliceUnitFactory)
    effective_date = factory.LazyFunction(lambda: fake.date_time_this_decade())
    end_date = factory.LazyFunction(lambda: fake.date_time_this_decade())


class InvolvementFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Involvement

    allegation = factory.SubFactory(AllegationFactory)
    officer = factory.SubFactory(OfficerFactory)


class AttachmentFileFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = AttachmentFile

    allegation = factory.SubFactory(AllegationFactory)
    additional_info = factory.LazyFunction(lambda: {'info': fake.word()})
    original_url = factory.LazyFunction(lambda: fake.url())


class AttachmentRequestFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = AttachmentRequest

    allegation = factory.SubFactory(AllegationFactory)
    email = factory.LazyFunction(lambda: fake.email())


class VictimFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Victim

    allegation = factory.SubFactory(AllegationFactory)
    gender = factory.LazyFunction(lambda: random.choice(['M', 'F']))
    race = 'Black'
    age = FuzzyInteger(18, 60)


class PoliceWitnessFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = PoliceWitness

    allegation = factory.SubFactory(AllegationFactory)
    gender = factory.LazyFunction(lambda: random.choice(['M', 'F']))
    race = 'Black'
    officer = factory.SubFactory(OfficerFactory)
