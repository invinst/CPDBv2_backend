import random
from datetime import datetime

import pytz

from django.contrib.gis.geos import MultiPolygon, Polygon, MultiLineString, LineString

import factory
from factory.fuzzy import FuzzyInteger
from faker import Faker

from data.models import (
    Area, Investigator, LineArea, Officer, OfficerBadgeNumber, PoliceUnit, Allegation, OfficerAllegation,
    Complainant, OfficerHistory, AllegationCategory, Involvement, AttachmentFile, AttachmentRequest, Victim,
    PoliceWitness, InvestigatorAllegation, RacePopulation, Award, Salary, OfficerYearlyPercentile,
    OfficerAlias
)
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


class RacePopulationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = RacePopulation


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


class PoliceUnitFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = PoliceUnit

    unit_name = factory.LazyFunction(lambda: fake.numerify(text="###"))
    description = factory.LazyFunction(lambda: fake.text(25))


class OfficerFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Officer

    first_name = factory.LazyFunction(lambda: fake.first_name())
    last_name = factory.LazyFunction(lambda: fake.last_name())
    gender = factory.LazyFunction(lambda: random.choice(['M', 'F']))
    race = 'White'
    appointed_date = factory.LazyFunction(lambda: fake.date())
    rank = factory.LazyFunction(lambda: fake.word())
    birth_year = factory.LazyFunction(lambda: random.randint(1900, 2000))
    active = factory.LazyFunction(lambda: random.choice(ACTIVE_CHOICES)[0])
    tags = factory.LazyFunction(lambda: fake.pylist(2, False, str))
    complaint_percentile = factory.LazyFunction(lambda: fake.pyfloat(left_digits=2, right_digits=1, positive=True))


class InvestigatorFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Investigator

    first_name = factory.LazyFunction(lambda: fake.name())
    last_name = factory.LazyFunction(lambda: fake.name())


class AllegationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Allegation

    crid = factory.LazyFunction(lambda: str(random.randint(100000, 999999)))

    # required for percentile calculation, we ensure all objects factoried in same data range
    incident_date = factory.LazyFunction(lambda: fake.date_time_between_dates(
        datetime_start=datetime(2000, 1, 1, tzinfo=pytz.utc),
        datetime_end=datetime(2016, 12, 31, tzinfo=pytz.utc),
        tzinfo=pytz.utc
    ))
    point = None

    @factory.post_generation
    def areas(self, create, extracted, **kwargs):
        if not create:  # Simple build, do nothing.
            return
        if extracted:   # A list of groups were passed in, use them
            for area in extracted:
                self.areas.add(area)


class InvestigatorAllegationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = InvestigatorAllegation

    investigator = factory.SubFactory(InvestigatorFactory)
    allegation = factory.SubFactory(AllegationFactory)


class AllegationCategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = AllegationCategory


class OfficerAllegationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = OfficerAllegation

    allegation = factory.SubFactory(AllegationFactory)
    officer = factory.SubFactory(OfficerFactory)
    start_date = factory.LazyFunction(lambda: fake.date())
    final_finding = factory.LazyFunction(lambda: random.choice(['SU', 'NS']))
    final_outcome = factory.LazyFunction(
        lambda: random.choice(['27 Day Suspension', '28 Day Suspension', 'No Action Taken'])
    )
    allegation_category = factory.SubFactory(AllegationCategoryFactory)


class OfficerBadgeNumberFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = OfficerBadgeNumber

    officer = factory.SubFactory(OfficerFactory)
    star = factory.LazyFunction(lambda: str(random.randint(10000, 99999)))
    current = factory.LazyFunction(lambda: fake.boolean())


class ComplainantFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Complainant

    allegation = factory.SubFactory(AllegationFactory)
    gender = factory.LazyFunction(lambda: random.choice(['M', 'F']))
    race = 'Black'
    age = FuzzyInteger(18, 60)


class OfficerHistoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = OfficerHistory

    officer = factory.SubFactory(OfficerFactory)
    unit = factory.SubFactory(PoliceUnitFactory)
    effective_date = factory.LazyFunction(lambda: fake.date_time_this_decade(tzinfo=pytz.utc))
    end_date = factory.LazyFunction(lambda: fake.date_time_this_decade(tzinfo=pytz.utc))


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
    source_type = factory.LazyFunction(lambda: fake.word())
    external_id = factory.LazyFunction(lambda: fake.word())
    title = factory.LazyFunction(lambda: fake.sentence())
    external_created_at = factory.LazyFunction(lambda: fake.date_time_this_decade(tzinfo=pytz.utc))
    text_content = factory.LazyFunction(lambda: fake.text(64))
    views_count = factory.LazyFunction(lambda: random.randint(0, 99999))
    downloads_count = factory.LazyFunction(lambda: random.randint(0, 99999))
    show = factory.LazyFunction(lambda: fake.boolean())


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
    officer = factory.SubFactory(OfficerFactory)


class AwardFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Award

    officer = factory.SubFactory(OfficerFactory)
    award_type = factory.LazyFunction(lambda: random.choice(['Life Saving Award', 'Complimentary Letter']))
    start_date = factory.LazyFunction(lambda: fake.date_time_this_decade(tzinfo=pytz.utc))
    end_date = factory.LazyFunction(lambda: fake.date_time_this_decade(tzinfo=pytz.utc))
    request_date = factory.LazyFunction(lambda: fake.date_time_this_decade(tzinfo=pytz.utc))
    rank = factory.LazyFunction(lambda: fake.word())
    last_promotion_date = factory.LazyFunction(lambda: fake.date_time_this_decade(tzinfo=pytz.utc))
    ceremony_date = factory.LazyFunction(lambda: fake.date_time_this_decade(tzinfo=pytz.utc))


class SalaryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Salary

    pay_grade = factory.LazyFunction(lambda: random.choice(['SR|9796', 'EX|9782', 'D|1]']))
    rank = factory.LazyFunction(lambda: fake.word())
    salary = factory.LazyAttribute(lambda _: fake.pyint())
    employee_status = factory.LazyFunction(lambda: fake.word())
    org_hire_date = factory.LazyFunction(lambda: fake.date_this_decade())
    spp_date = factory.LazyFunction(lambda: fake.date_this_decade())
    start_date = factory.LazyFunction(lambda: fake.date_this_decade())
    year = factory.LazyFunction(lambda: fake.year())
    age_at_hire = factory.LazyAttribute(lambda _: fake.pyint())
    officer = factory.SubFactory(OfficerFactory)


class OfficerYearlyPercentileFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = OfficerYearlyPercentile

    officer = factory.SubFactory(OfficerFactory)
    year = factory.LazyFunction(lambda: fake.year())


class OfficerAliasFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = OfficerAlias

    new_officer = factory.SubFactory(OfficerFactory)
